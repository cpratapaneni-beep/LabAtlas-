"""Step 6: a wet/dry setting for the profiles merge.py added, from the published model, without touching anyone
already in the atlas.

The model is fitted on the base atlas (the one the published accuracy was measured on) with the new people
appended, so everyone else's training data is unchanged; only the new people's predictions are written back.

  python3 classify_new.py <base atlas.html> <merged atlas.html>
"""
import json, os, re, subprocess, sys, tempfile
base, merged = sys.argv[1:3]
repo = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def load(path):
    t = open(path, encoding='utf-8').read()
    m = re.search(r'(<script id="atlasdata" type="application/json">)(.*?)(</script>)', t, re.S)
    return t, m, json.loads(m.group(2))
tb, mb, db = load(base); tm, mm, dm = load(merged)
new = [i for i, p in enumerate(dm['pis']) if p.get('v118') == 'mentor']
assert new == list(range(len(db['pis']), len(db['pis']) + len(new))), 'new people must follow the base investigators'
T = db['pnames']; idx = {x: i for i, x in enumerate(T)}
def ti(x):
    if x not in idx: idx[x] = len(T); T.append(x)
    return idx[x]
for i in new:
    q = json.loads(json.dumps(dm['pis'][i])); q['p'] = [[ti(dm['pnames'][e[0]]), e[1], e[2], e[3]] for e in q['p']]
    db['pis'].append(q)
db['$pack']['pnamesLen'] = len(T)
tmp = tempfile.mkdtemp()
with open(os.path.join(tmp, 'atlas.html'), 'w', encoding='utf-8') as f:
    f.write(tb[:mb.start(2)] + json.dumps(db, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + tb[mb.end(2):])
ml = os.path.join(repo, 'ml')
subprocess.run([sys.executable, os.path.join(ml, 'wetdry.py'), 'predict', '--data', os.path.join(tmp, 'atlas.html'),
                '--split', os.path.join(ml, 'split.json'), '--labels', os.path.join(ml, 'gold_labels.csv'),
                '--extra', os.path.join(ml, 'gold_labels_dept.csv'), '--out', os.path.join(tmp, 'pred.json')], check=True)
P = json.load(open(os.path.join(tmp, 'pred.json')))['people']
for k, i in enumerate(new):
    q, x = P[len(P) - len(new) + k], dm['pis'][i]
    for f in ('l', 'c', 'cf', 'ev'):
        if f in q: x[f] = q[f]
    x['ev'] = dict(x.get('ev') or {}, added='v118: added from the undergraduate mentor records and PubMed')
open(merged, 'w', encoding='utf-8').write(tm[:mm.start(2)] + json.dumps(dm, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + tm[mm.end(2):])
print(len(new), 'new profiles classified')
