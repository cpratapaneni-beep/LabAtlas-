"""Phase C: keep a PubMed paper for an investigator only when one of its authors is that person by name (surname
equal, given name starting with theirs) AND that author's own listed affiliation is Emory or a partner. The
paper-level [ad] filter used to search matches any author on the paper; this is the per-author check.

Writes verified.json: {"pi": {idx: [pmid, ...]}, "mentor": {name: {"pmids": [...], "affs": [...]}}} and a report."""
import json, re, sys, unicodedata, collections
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from names import parts

EMORY = re.compile(r"emory|children'?s healthcare of atlanta|choa\b|yerkes|winship|grady (memorial|health)|rollins school of public health|atlanta va|atlanta veterans", re.I)


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z]+', '', s)


def given_ok(fore, initials, first):
    f = norm(first.split()[0]) if first else ''
    fo = (fore or '').replace('.', ' ').split()
    if fo:
        g = norm(fo[0])
        if len(g) > 1 and len(f) > 1:
            return g == f or (g.startswith(f) and len(f) >= 4) or (f.startswith(g) and len(g) >= 4)
        # "A Alfred" style: an initial in the record, compare initials
        return bool(g) and bool(f) and g[0] == f[0] and len(fo) > 1 and norm(fo[1]).startswith(norm(first.split()[-1])[:3])
    return False


def author_match(rec, last, firsts):
    L = norm(last)
    hits = []
    for a in rec['authors']:
        al = norm(a[0])
        if not al or (al != L and not (len(L) > 5 and (al.endswith(L) or L.endswith(al)))):
            continue
        if any(given_ok(a[1], a[2], f) for f in firsts):
            hits.append(a)
    return hits


def run(search_file, rec_index, key):
    out, why = {}, collections.Counter()
    for l in open(search_file):
        r = json.loads(l)
        pr = parts(r['n'])
        if not pr or not r.get('ids'):
            continue
        last, firsts = pr
        keep, affs = [], []
        for pm in r['ids']:
            rec = rec_index.get(str(pm))
            if not rec:
                why['no record'] += 1; continue
            hits = author_match(rec, last, firsts)
            if not hits:
                why['name not on the paper'] += 1; continue
            own = [af for a in hits for af in a[3]]
            if not own:
                why['author has no affiliation listed'] += 1; continue
            if not any(EMORY.search(af) for af in own):
                why['author not at Emory on this paper'] += 1; continue
            why['kept'] += 1
            keep.append(int(pm)); affs.extend(af for af in own if EMORY.search(af))
        if keep:
            out[r['i'] if key == 'pi' else r['n']] = {'pmids': keep, 'affs': affs[:40]}
    return out, why


if __name__ == '__main__':
    recs = {}
    for l in open('records.jsonl'):
        r = json.loads(l); recs[r['pmid']] = r
    pi, why_pi = run('search.jsonl', recs, 'pi')
    mentor, why_m = run('mentor_search.jsonl', recs, 'mentor')
    json.dump({'pi': pi, 'mentor': mentor}, open('verified.json', 'w'))
    print('investigators:', dict(why_pi), '| people with papers:', len(pi))
    print('mentors:', dict(why_m), '| people with papers:', len(mentor))
