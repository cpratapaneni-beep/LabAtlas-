"""Same-name check: when an investigator's verified papers carry incompatible middle initials (e.g. "Mary G" and
"Mary E" Lynch, both at Emory), keep only the initial family that the papers already on file use; papers with no
middle initial are kept only if already on file. With nothing on file to anchor it, nothing new is added for that
person. Writes verified2.json and disambig_report.txt."""
import json, collections, re
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import parts, author_match
R = {}
for l in open('records.jsonl'):
    r = json.loads(l); R[r['pmid']] = r
V = json.load(open('verified.json')); names = json.load(open('pi_names.json')); ex = json.load(open('pi_existing_pmids.json'))
def mid(fore):
    t = (fore or '').replace('.', ' ').replace('-', ' ').split()
    return ''.join(x[0].upper() for x in t[1:]) if len(t) > 1 else ''
def compat(a, b): return a.startswith(b) or b.startswith(a)
rep = []
def clean(key, name, pmids, onfile):
    last, firsts = parts(name)
    m = {}
    for pm in pmids:
        hits = author_match(R[str(pm)], last, firsts)
        m[pm] = mid(hits[0][1]) if hits else ''
    fams = []   # families of mutually compatible initials, with paper counts
    for mi, n in collections.Counter(x for x in m.values() if x).most_common():
        for f in fams:
            if all(compat(mi, y) for y in f['m']): f['m'].add(mi); f['n'] += n; break
        else: fams.append({'m': {mi}, 'n': n})
    big = [f for f in fams if f['n'] >= 3]
    if len(big) < 2: return pmids
    # the atlas name's own middle initial, when it has one, decides first
    toks = [x for x in re.sub(r'\([^)]*\)', ' ', name).replace(',', ' ').split() if x]
    own = ''.join(x[0].upper() for x in toks[1:-1] if re.fullmatch(r'[A-Za-z]\.?', x))
    if own:
        hit = [k for k, f in enumerate(big) if any(compat(own, y) for y in f['m'])]
        if len(hit) == 1:
            keep = big[hit[0]]['m']
            out = [pm for pm in pmids if pm in onfile or (m[pm] and any(compat(m[pm], y) for y in keep))]
            rep.append('%s: kept middle initial %s (the atlas name has it); %d papers under other initials left out' % (name, ','.join(sorted(keep)), len(pmids) - len(out)))
            return out
    anchor = collections.Counter()
    for pm in pmids:
        if pm in onfile and m[pm]:
            for k, f in enumerate(big):
                if any(compat(m[pm], y) for y in f['m']): anchor[k] += 1
    if not anchor:
        rep.append('%s: papers under %s, nothing on file to tell them apart: no new papers added' % (name, ' / '.join(','.join(sorted(f['m'])) for f in big)))
        return [pm for pm in pmids if pm in onfile]
    keep = big[anchor.most_common(1)[0][0]]['m']
    out = [pm for pm in pmids if pm in onfile or (m[pm] and any(compat(m[pm], y) for y in keep))]
    rep.append('%s: kept middle initial %s (matches the papers on file); %d papers under other initials left out' % (name, ','.join(sorted(keep)), len(pmids) - len(out)))
    return out
V2 = {'pi': {}, 'mentor': V['mentor']}
for k, v in V['pi'].items():
    i = int(k); V2['pi'][k] = dict(v, pmids=clean(k, names[i], v['pmids'], set(ex[i])))
json.dump(V2, open('verified2.json', 'w'))
open('disambig_report.txt', 'w').write('\n'.join(sorted(rep)) + '\n')
print(len(rep), 'investigators adjusted'); print('\n'.join(sorted(rep)[:40]))
