"""Write the wet/dry model's output into the atlas data.

Reads the atlas (HTML file, or the JSON inside it), the predictions written by
`wetdry.py predict` and the locked-test report written by `wetdry.py evaluate`,
and writes an atlas whose records carry the new state (l), P(wet) as a
percentage (c), the confidence that the call is right as a percentage (cf)
and the evidence (ev). The upstream classifier's original label
stays in l0/c0 untouched, and the keyword score's state (v3.1) is kept in l31. A top-level `wd` block records the model version, its
bands and the accuracy measured on the locked test set, so the page can quote
measured numbers instead of stated ones.

  python apply_wetdry.py atlas.html predictions.json report/evaluation.csv -o atlas_wd.html \
      [--departments report/departments.json] [--confidence report/confidence.json]
"""
import argparse
import csv
import datetime
import json
import re
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('atlas')
    ap.add_argument('predictions')
    ap.add_argument('evaluation')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--departments', help='departments.json from department_report.py')
    ap.add_argument('--confidence', help='confidence.json from wetdry.py evaluate (how the confidence held up on the test set)')
    a = ap.parse_args()

    src = open(a.atlas, encoding='utf-8').read()
    m = re.search(r'(<script[^>]*id="atlasdata"[^>]*>)(.*?)(</script>)', src, re.S)
    if m:
        head, body, tail = src[:m.start(2)], m.group(2), src[m.end(2):]
    else:
        head, body, tail = '', src, ''
    D = json.loads(body)
    pred = json.load(open(a.predictions))
    P = D['pis']
    if len(pred['people']) != len(P):
        sys.exit('predictions cover %d records, atlas has %d' % (len(pred['people']), len(P)))

    # keep the keyword score's label (v3.1) so the model can be re-measured
    # against it from this file; an atlas that already carries model labels
    # without that copy has lost it and cannot serve as a source
    if 'wd' in D and any('l31' not in p for p in P):
        sys.exit('this atlas already carries model labels and no copy of the v3.1 label (l31); '
                 'build from a pre-model atlas or from v79 or later')
    for p, q in zip(P, pred['people']):
        p.setdefault('l31', p['l'])
        p['l'] = q['l']
        p['c'] = q['c'] if q['l'] else None
        p['cf'] = q.get('cf') if q['l'] else None
        p['ev'] = q['ev']
        p['cr'] = p['cr'] if p.get('status') else 'wet/dry model ' + pred['model']

    ev = {}
    for r in csv.DictReader(open(a.evaluation)):
        ev[r['metric']] = {k: round(float(v), 4) for k, v in r.items() if k != 'metric'}
    counts = {}
    for p in P:
        counts[p['l']] = counts.get(p['l'], 0) + 1
    D['wd'] = {
        'model': pred['model'],
        'bands': pred['bands'],
        'trained_on': pred['trained_on'],
        'generated': datetime.date.today().isoformat(),
        'test': ev,
        'top_wet_terms': pred['top_wet_terms'][:12],
        'top_dry_terms': pred['top_dry_terms'][:12],
    }
    if 'confidence' in pred:
        D['wd']['conf'] = dict(pred['confidence'])
        if a.confidence:
            D['wd']['conf']['test'] = json.load(open(a.confidence))['test']
    if a.departments:
        dep = json.load(open(a.departments))
        if len(dep['units']) != len(D['depts']):
            sys.exit('departments.json covers %d units, atlas has %d' % (len(dep['units']), len(D['depts'])))
        D['wd']['depts'] = dep
    out = json.dumps(D, ensure_ascii=False, separators=(',', ':'))
    # keep the JSON safe inside a <script> element
    out = out.replace('</', '<\\/')
    open(a.out, 'w', encoding='utf-8').write(head + out + tail)
    print('states', dict(sorted(counts.items())), '->', a.out)


if __name__ == '__main__':
    main()
