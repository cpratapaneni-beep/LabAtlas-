"""Department-by-department view of the wet/dry labels.

For every unit in the atlas: its hand-assigned research character
(department_types.csv), how its investigators come out on the wet/dry axis,
how many of them were read and labelled by hand, and how often the model
agreed with the hand label on the locked test set. Writes a Markdown report
and a CSV, and a compact per-unit block that apply_wetdry.py stores in the page.

  python ml/department_report.py atlas.html predictions.json ml/report/test_predictions.csv \
      --labels ml/gold_labels.csv --extra ml/gold_labels_dept.csv --split ml/split.json --out ml/report
"""
import argparse
import collections
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wetdry as W  # noqa: E402

TYPE_NAME = {
    'basic_science': 'Basic science', 'translational_centre': 'Translational research centre',
    'engineering': 'Engineering', 'genetics': 'Genetics', 'clinical_lab': 'Pathology & laboratory medicine',
    'clinical': 'Clinical', 'population': 'Public & population health', 'quantitative': 'Quantitative',
    'behavioural_social': 'Behavioural & social science', 'nursing_education': 'Nursing', 'admin': 'Administrative',
}
SIDE = {0: 'none', 1: 'wet', 4: 'wet', 3: 'hybrid', 5: 'dry', 2: 'dry'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('atlas')
    ap.add_argument('predictions')
    ap.add_argument('test_predictions')
    ap.add_argument('--labels', required=True)
    ap.add_argument('--extra')
    ap.add_argument('--split', required=True)
    ap.add_argument('--types', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'department_types.csv'))
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    D = W.load_data(a.atlas)
    P = D['pis']
    types = W.load_dept_types(a.types, D)
    gold, train, test = W.load_gold(a.labels, a.split, D, a.extra)
    rand = set(json.load(open(a.split))['order'])
    pred = json.load(open(a.predictions))['people']
    tp = {int(r['index']): r for r in csv.DictReader(open(a.test_predictions))}

    units = []
    for u, dep in enumerate(D['depts']):
        mem = [i for i, p in enumerate(P) if u in (p.get('d') or [])]
        comp = collections.Counter(SIDE[pred[i]['l']] for i in mem)
        hand = [i for i in mem if i in gold]
        hand_rand = [i for i in hand if i in rand]
        tested = [i for i in mem if i in tp and tp[i]['gold'] in 'WHD']
        agree = sum(1 for i in tested if W.SIDE[int(tp[i]['new_state'])] == tp[i]['gold'])
        units.append({
            'index': u, 'institution': D['insts'][dep['i']]['k'], 'unit': dep['n'], 'type': types.get(u, ''),
            'members': len(mem), 'wet': comp['wet'], 'hybrid': comp['hybrid'], 'dry': comp['dry'],
            'unclassified': comp['none'], 'hand_labelled': len(hand),
            'hand_random': len(hand_rand), 'hand_targeted': len(hand) - len(hand_rand),
            'test_scored': len(tested), 'test_agree': agree,
        })

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, 'departments.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(units[0]))
        w.writeheader()
        w.writerows(units)

    # by research character, test agreement pooled over the people (each once)
    by = collections.defaultdict(lambda: collections.Counter())
    for i, r in tp.items():
        if r['gold'] not in 'WHD':
            continue
        ts = {types.get(u) for u in (P[i].get('d') or [])} or {''}
        for t in ts:
            by[t]['n'] += 1
            by[t]['ok'] += W.SIDE[int(r['new_state'])] == r['gold']
    lines = ['# The wet/dry axis, department by department', '',
             'Every unit was classified by hand by its research character (`department_types.csv`). '
             'That typing was used to choose which investigators to read and label next, and to report '
             'accuracy by department. It is **not** an input to any one person\'s call: tested as a model '
             'feature, it cost 3-4 points on the investigators who do not match their department (the '
             'physician-scientist with a bench lab in a clinical department, the pathologist listed in a '
             'basic-science programme), so each person is read from their own work.', '',
             '## Accuracy on the locked test set, by research character', '',
             '| research character | test investigators | model on the right side |', '|---|---|---|']
    for t, c in sorted(by.items(), key=lambda kv: -kv[1]['n']):
        if c['n']:
            lines.append('| %s | %d | %.0f%% (%d of %d) |' % (TYPE_NAME.get(t, t or 'no unit'), c['n'],
                                                              100 * c['ok'] / c['n'], c['ok'], c['n']))
    lines += ['', 'A person in several units counts once in each. Small groups carry wide uncertainty.', '',
              '## Every unit', '',
              '| unit | character | members | wet side | hybrid | dry side | unclassified | hand-labelled | test: right / scored |',
              '|---|---|---|---|---|---|---|---|---|']
    for x in sorted(units, key=lambda x: -x['members']):
        lines.append('| %s (%s) | %s | %d | %d | %d | %d | %d | %d | %s |' % (
            x['unit'], x['institution'], TYPE_NAME.get(x['type'], x['type']), x['members'], x['wet'],
            x['hybrid'], x['dry'], x['unclassified'], x['hand_labelled'],
            ('%d / %d' % (x['test_agree'], x['test_scored'])) if x['test_scored'] else '-'))
    open(os.path.join(a.out, 'departments.md'), 'w').write('\n'.join(lines) + '\n')

    # compact block for the page: per unit [type, hand-labelled, test scored, test agreed]
    json.dump({'types': TYPE_NAME, 'targeted': sum(1 for i in gold if i not in rand),
               'units': [[x['type'], x['hand_labelled'], x['test_scored'], x['test_agree']] for x in units]},
              open(os.path.join(a.out, 'departments.json'), 'w'), separators=(',', ':'))
    print('wrote', os.path.join(a.out, 'departments.md'))


if __name__ == '__main__':
    main()
