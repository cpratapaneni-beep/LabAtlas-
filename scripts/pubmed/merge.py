"""Phase D: put the verified PubMed papers into the atlas, and add the undergraduate mentors the original scrape
missed (people in an atlas department, by their own Emory affiliation on PubMed).

  python3 merge.py <in.html> <out.html> <report.md>

Nothing on file is removed. For each investigator:
- a verified paper already on file (same PMID) is left as it is;
- a title-only paper on file whose title matches a verified PubMed record gets that PMID and PubMed's year;
- any other verified paper is added, filed under the site's PubMed source ("matched by author affiliation").
Co-author links gain the newly shared papers. The 20 PMIDs with no PubMed record are cleared, so those titles
link to a title search instead of a dead page.
"""
import collections, json, os, re, sys, unicodedata
src_html, out_html, report_md = sys.argv[1:4]
t = open(src_html, encoding='utf-8').read()
m = re.search(r'(<script id="atlasdata" type="application/json">)(.*?)(</script>)', t, re.S)
d = json.loads(m.group(2))
pis, titles, pack = d['pis'], d['pnames'], d['$pack']
labels = pack['labels']
PUBMED = labels.index('NCBI PubMed / PUBMED_MATCHED_AUTHOR_AFFILIATION_OR_ORCID')
V = json.load(open('verified2.json'))
R = {}
for l in open('records.jsonl'):
    r = json.loads(l); R[r['pmid']] = r
Y = json.load(open(os.environ.get('PUBMED_YEARS', 'pubmed_years.json')))   # years.py: PubMed's record for every PMID already on file
norm = lambda s: re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()).strip()
tidx = {}
for i, ti in enumerate(titles):
    tidx.setdefault(ti, i)
def title_index(ti):
    if ti not in tidx:
        tidx[ti] = len(titles); titles.append(ti)
    return tidx[ti]
st = collections.Counter()
log = []

# ---- dead PMIDs: no PubMed record
for p in pis:
    for e in p.get('p', []):
        if isinstance(e[3], int) and not (Y.get(str(e[3])) or {}).get('title'):
            e[3] = ''; st['dead PMIDs cleared'] += 1

# ---- add / upgrade
def add_papers(p, pmids):
    have = {e[3] for e in p.get('p', []) if isinstance(e[3], int)}
    bare = {}
    for e in p.get('p', []):
        if not isinstance(e[3], int):
            bare.setdefault(norm(titles[e[0]])[:70], e)
    added = upgraded = 0
    for pm in sorted(set(pmids), key=lambda x: -((R.get(str(x)) or {}).get('year') or 0)):
        if pm in have: continue
        r = R.get(str(pm))
        if not r or not r.get('title'): continue
        key = norm(r['title'])[:70]
        if key in bare and len(key) > 20:
            e = bare.pop(key); e[3] = int(pm)
            if r.get('year'): e[2] = r['year']
            upgraded += 1
        else:
            p.setdefault('p', []).append([title_index(r['title']), PUBMED, r.get('year'), int(pm)])
            added += 1
        have.add(pm)
    return added, upgraded
before = sum(len(p.get('p', [])) for p in pis)
grew = collections.Counter()
for k, v in V['pi'].items():
    a, u = add_papers(pis[int(k)], v['pmids'])
    st['papers added'] += a; st['title-only papers given their PMID'] += u
    if a: grew[int(k)] = a

# ---- missed faculty from the mentors
DEPTS, INSTS = d['depts'], d['insts']
inst_k = [x['k'] for x in INSTS]
STOP = {'and', 'of', 'the', 'dept', 'department', 'division', 'program', 'school', 'emory', 'university'}
SYN = {'laboratory': 'lab', 'sciences': 'science', 'behavioural': 'behavioral', 'med': 'medicine'}
def dtoks(x):
    w = re.findall(r'[a-z]+', unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode().lower().replace('&', ' and '))
    return frozenset(SYN.get(t, t) for t in w if t not in STOP)
DT = [dtoks(x['n']) for x in DEPTS]
INST_HINT = [('SOM', r'school of medicine'), ('RSPH', r'rollins|school of public health'), ('Nursing', r'school of nursing'),
             ('EPC', r'yerkes|primate'), ('Winship', r'winship'), ('CHOA', r"children'?s healthcare of atlanta"), ('Vaccine', r'vaccine center')]
DEPT_RE = re.compile(r"(?:Department|Dept\.?) of ([A-Z][A-Za-z&,'\- ]+?)(?=,|;|\.|$| at )")
DEPT_RE2 = re.compile(r"(?:^|, )([A-Z][A-Za-z&'\- ]+?) Department\b")
def aff_depts(af):
    out = [dtoks(g) for g in DEPT_RE.findall(af)] + [dtoks(g) for g in DEPT_RE2.findall(af)]
    inst = [k for k, rx in INST_HINT if re.search(rx, af, re.I)]
    return [x for x in out if x], (inst[0] if inst else 'ECAS')
def pick_dept(affs, fields):
    """fields: token sets of the thesis departments this mentor advised in (may be empty)."""
    pairs = collections.Counter()
    for af in affs:
        ds, inst = aff_depts(af)
        for dk in ds:
            pairs[(dk, inst)] += 1
    # a department matching the fields this person advised theses in comes first (it separates namesakes);
    # otherwise the most frequent department on their own papers
    ranked = sorted(pairs.items(), key=lambda kv: (not (fields and any(kv[0][0] & f for f in fields)), -kv[1]))
    for (dk, inst), c in ranked:
        exact = [j for j, t in enumerate(DT) if t == dk]
        near = [j for j, t in enumerate(DT) if t and (t <= dk or dk <= t)]
        for cands in (exact, near):
            if not cands: continue
            same = [j for j in cands if inst_k[DEPTS[j]['i']] == inst]
            if same: return same[0], pairs
            if len({DEPTS[j]['i'] for j in cands}) == 1: return cands[0], pairs
    return None, pairs
# last year each outside mentor took a student (symposium books and honors theses)
H0 = json.loads(re.search(r'<script id="surehist" type="application/json">(.*?)</script>', t, re.S).group(1))
mentor_last = collections.Counter()
for mm in H0['mentors']:
    if mm.get('pi_id') is None:
        mentor_last[norm(mm['name'])] = max([x['y'] for x in mm['records']] or [0])
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etd_honors as E
for l in open(os.environ.get('ETD_RECORDS', 'build/etd/records.jsonl')):   # etd_honors.py crawl output
    r = json.loads(l)
    if 'error' in r or 'honors' not in ''.join(r.get('submission') or []).lower(): continue
    mt = re.match(r'\w+\s+(\d{4})', r.get('term') or ''); y = int(mt.group(1)) if mt else (r.get('year') or 0)
    for raw in r.get('chair') or []:
        nm, _ = E.advisor(raw)
        if nm: mentor_last[norm(nm)] = max(mentor_last[norm(nm)], y)
# one person can appear under two spellings ("Anna Kenney", "Anna M. Kenney"): group by surname + first name
import names as _names
ns = {'parts': _names.parts}
groups = collections.defaultdict(list)
for name in V['mentor']:
    pr = ns['parts'](name)
    if not pr: continue
    k = (norm(pr[0]), norm(pr[1][0].split()[0]))
    for g in list(groups):      # same surname, one first name the start of the other (Krish / Krishnankutty)
        if g[0] == k[0] and min(len(g[1]), len(k[1])) >= 4 and (g[1].startswith(k[1]) or k[1].startswith(g[1])):
            k = g; break
    groups[k].append(name)
existing = {}
for i, p in enumerate(pis):
    pr = ns['parts'](p['n'])
    if pr: existing[(norm(pr[0]), norm(pr[1][0].split()[0]))] = i
outside = {o['name']: o for o in json.load(open('outside_mentors.json'))}
added_people = []
for key, variants in sorted(groups.items()):
    name = max(variants, key=lambda x: (len(x.split()), len(x)))
    if key in existing:
        log.append((name, 'already in the atlas as ' + pis[existing[key]]['n'])); continue
    pms = sorted({pm for v in variants for pm in V['mentor'][v]['pmids']})
    affs = [a for v in variants for a in V['mentor'][v]['affs']]
    recs = [R[str(x)] for x in pms if str(x) in R]
    if len(recs) < 3:
        log.append((name, 'fewer than 3 Emory-affiliated papers')); continue
    last = norm(key[0])
    senior = sum(1 for r in recs if r['authors'] and norm(r['authors'][-1][0]) == last)
    if not senior:
        log.append((name, 'never the senior (last) author: likely a trainee, not a lab head')); continue
    yrs = [r['year'] for r in recs if r.get('year')]
    lastm = max(mentor_last.get(norm(v), 0) for v in variants)
    if (max(yrs) if yrs else 0) < 2021 and lastm < 2023:
        log.append((name, 'no Emory paper since %s and last mentored %s: likely no longer at Emory' % (max(yrs) if yrs else '?', lastm or '?'))); continue
    hon = collections.Counter()
    for v in variants:
        hon.update((outside.get(v) or {}).get('hon_depts') or {})
    if hon and not any(E.LAB_FIELDS.search(h) and not E.NOT_LAB.search(h) for h in hon):
        log.append((name, 'advised theses only in ' + ', '.join(hon) + ': not a lab field in the atlas; PubMed papers under this name are likely a namesake')); continue
    fields = [dtoks(h) for h in hon if E.LAB_FIELDS.search(h) and not E.NOT_LAB.search(h)]
    fields = [f | ({'biology', 'neuroscience', 'behavioral'} if 'neuroscience' in f else set()) for f in fields]
    hit, deps = pick_dept(affs, fields)
    if hit is None:
        log.append((name, 'department not one of the atlas units: ' + (', '.join(' '.join(sorted(x[0])) for x in list(deps)[:3]) or 'none named'))); continue
    # only papers where this person's own affiliation names the chosen department, or names none
    import verify as _v
    vns = {'parts': _v.parts, 'author_match': _v.author_match}
    pr = vns['parts'](name); want = DT[hit]
    def mine(r):
        for a in vns['author_match'](r, pr[0], pr[1]):
            ds = [dk for af in a[3] for dk in aff_depts(af)[0]]
            if not ds or any(dk & want for dk in ds): return True
        return False
    kept = [r for r in recs if mine(r)]
    if len(kept) < 3:
        log.append((name, 'fewer than 3 papers from %s once other departments are set aside' % DEPTS[hit]['n'])); continue
    if len(kept) < len(recs): st['papers left out of new profiles (other department)'] += len(recs) - len(kept)
    recs = kept; yrs = [r['year'] for r in recs if r.get('year')]
    if (max(yrs) if yrs else 0) < 2021 and lastm < 2023:
        log.append((name, 'no paper from %s since %s and last mentored %s: likely no longer at Emory' % (DEPTS[hit]['n'], max(yrs) if yrs else '?', lastm or '?'))); continue
    senior = sum(1 for r in recs if r['authors'] and norm(r['authors'][-1][0]) == last)
    pubs = [[title_index(r['title']), PUBMED, r.get('year'), int(r['pmid'])] for r in sorted(recs, key=lambda r: -(r.get('year') or 0))]
    p = {'n': name, 'i': [DEPTS[hit]['i']], 'd': [hit], 'l': 0, 'g': '', 'e': '', 'c': None,
         'cr': pis[0].get('cr'), 'w': [], 'p': pubs, 'l0': 0, 'c0': None,
         'ev': {'model': (pis[0].get('ev') or {}).get('model'), 'P': None, 'n_titles': len(pubs), 'n_grants': 0,
                'why_unclassified': 'added in v118 from the undergraduate mentor records and PubMed; not yet classified'},
         'l31': 0, 'cf': None, 's': [], 'v118': 'mentor', 'v118names': variants}
    existing[key] = len(pis); pis.append(p)
    DEPTS[hit]['c'] = DEPTS[hit].get('c', 0) + 1
    added_people.append((name, inst_k[DEPTS[hit]['i']] + ' ' + DEPTS[hit]['n'], len(pubs), senior, (min(yrs), max(yrs)) if yrs else None))
st['people added'] = len(added_people)

# ---- co-author links from shared PMIDs
by_pm = collections.defaultdict(set)
for i, p in enumerate(pis):
    for e in p.get('p', []):
        if isinstance(e[3], int): by_pm[e[3]].add(i)
pair = {(min(a, b), max(a, b)): set(ps) for a, b, ps in d['pubs']}
new_pairs = new_titles = 0
for pm, who in by_pm.items():
    if len(who) < 2 or len(who) > 25: continue
    r = R.get(str(pm)) or {}
    ti = None
    for a in who:
        for e in pis[a]['p']:
            if e[3] == pm: ti = e[0]; break
        if ti is not None: break
    who = sorted(who)
    for x in range(len(who)):
        for y in range(x + 1, len(who)):
            k = (who[x], who[y])
            if k not in pair: pair[k] = set(); new_pairs += 1
            if ti not in pair[k]: pair[k].add(ti); new_titles += 1
d['pubs'] = [[a, b, sorted(ps)] for (a, b), ps in sorted(pair.items())]
st['new co-author pairs'] = new_pairs; st['shared papers added to pairs'] = new_titles
pack['pnamesLen'] = len(titles)          # shared titles can now sit anywhere in the title table

after = sum(len(p.get('p', [])) for p in pis)
st['papers before'] = before; st['papers after'] = after
out = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
assert json.loads(out) == d
t = t[:m.start(2)] + out + t[m.end(2):]

# the per-person link and clinician tables get a blank row for each person added
for key, blank in (('atlaslinks', {'fu': None, 'fsrc': 'added v118', 'former': 0, 'fd': None, 'fds': None}), ('atlasphys', None)):
    mm = re.search(r'(<script id="%s" type="application/json">)(.*?)(</script>)' % key, t, re.S)
    j = json.loads(mm.group(2)); j['people'].extend([blank] * len(added_people))
    o = json.dumps(j, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    t = t[:mm.start(2)] + o + t[mm.end(2):]
open(out_html, 'w', encoding='utf-8').write(t)

with open(report_md, 'w') as f:
    f.write('# Publications re-collected from PubMed (v118)\n\n')
    for k, v in st.items(): f.write('- %s: %s\n' % (k, f'{v:,}' if isinstance(v, int) else v))
    f.write('\n## Faculty added from the undergraduate mentor records (%d)\n\n' % len(added_people))
    for a in sorted(added_people): f.write('- %s: %s; %d papers, senior author on %d%s\n' % (a[0], a[1], a[2], a[3], ', %d-%d' % a[4] if a[4] else ''))
    f.write('\n## Mentors checked and not added\n\n')
    for n, why in sorted(log): f.write('- %s: %s\n' % (n, why))
print(dict(st))
