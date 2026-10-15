"""Step 0: from the atlas, write the inputs of the PubMed scripts into the working directory:
  pi_names.json          every investigator's name, in atlas order
  pi_existing_pmids.json the PubMed IDs already on each record (used to settle same-name cases)
  outside_mentors.json   undergraduate mentors with no atlas profile (symposium books and honors theses)

  python3 prep.py <atlas.html> <etd records.jsonl>
"""
import collections, json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, '..'))
from symposium_scrape import Names, read_atlas, tokens
import etd_honors as E
atlas, etd = sys.argv[1:3]
t = open(atlas, encoding='utf-8').read()
d = json.loads(re.search(r'<script id="atlasdata" type="application/json">(.*?)</script>', t, re.S).group(1))
json.dump([p['n'] for p in d['pis']], open('pi_names.json', 'w'))
json.dump([[e[3] for e in p.get('p', []) if isinstance(e[3], int)] for p in d['pis']], open('pi_existing_pmids.json', 'w'))
pis, vocab, H, page = read_atlas(atlas)
names = Names(pis, vocab)
out = collections.OrderedDict()
for m in H['mentors']:
    if m.get('pi_id') is None:
        o = out.setdefault(m['name'], {'name': m['name'], 'sym': 0, 'hon': 0, 'hon_depts': collections.Counter()})
        o['sym'] += sum(1 for r in m['records'] if r.get('program') != 'Honors')
for l in open(etd):
    r = json.loads(l)
    if 'error' in r or 'honors' not in ''.join(r.get('submission') or []).lower() or (r.get('school') or [''])[0] != 'Emory College':
        continue
    for raw in r.get('chair') or []:
        nm, emory = E.advisor(raw)
        if not nm or len(tokens(nm)) < 2 or not emory or names.match(nm)[0] is not None:
            continue
        o = out.setdefault(nm, {'name': nm, 'sym': 0, 'hon': 0, 'hon_depts': collections.Counter()})
        o['hon'] += 1; o['hon_depts'][(r.get('dept') or [''])[0]] += 1
L = list(out.values())
for o in L: o['hon_depts'] = dict(o['hon_depts'])
json.dump(L, open('outside_mentors.json', 'w'), ensure_ascii=False)
print(len(d['pis']), 'investigators;', len(L), 'mentors outside the atlas')
