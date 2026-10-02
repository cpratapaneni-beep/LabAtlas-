#!/usr/bin/env python3
"""
Fix the errors in the atlas data that can be fixed with certainty from the
file alone, and write down every change.

    python3 clean_atlas_data.py in.html out.html [--log folder]

Used as a module by the build (clean(D) -> log). Everything it does is listed
below, and nothing it does depends on a guess:

  names     a degree fused onto the surname ("Michael ChungAB") is split off
            and kept with the degrees; a name held entirely in capitals is
            written in the ordinary way
  people    the same person entered twice is merged, from the explicit list
            MERGES below, each with the evidence that decided it. Two records
            that only look alike are left alone and listed for review instead.
  bios      a text shared word for word by several people is site boilerplate
            (Emory Healthcare's legal disclaimer, a navigation menu), not a
            description of any of them, and is removed
  papers    one work listed twice for one person is listed once, the better-
            sourced copy kept; a PMID attached to two different titles is taken
            off the unsourced copy; stray HTML entities are removed; a co-author
            link that names a paper one side does not list is dropped
  grants    stray whitespace left by the old 110-character cut is trimmed, and
            the co-grant links are rebuilt from the trimmed titles

What it cannot fix is also said plainly: the NIH dollar figures and grant
counts disagree with each other in ways that only NIH RePORTER can settle
(see nih_reporter_verify.py), and it cannot tell a namesake's paper from a
person's own.
"""
import collections
import csv
import html
import json
import os
import re
import sys

DEGREE = ('AB BA BS BSc BE JD DVM EdD ScM MB MBA MPA MPH MS MSc MA PhD MD DO RN '
          'DrPH MSN DNP PharmD DDS DMD').split()
GLUED = re.compile(r'^(?P<base>.*[a-z])(?P<deg>' + '|'.join(sorted(DEGREE, key=len, reverse=True)) + r')$')
DISCLAIMER = 'This website is provided as a courtesy to those interested in Emory Healthcare'

# (primary email or name, merged-in email or name, evidence). The primary keeps
# its name; the other name and email are kept as aliases so both still find the
# person. Each pair was checked by hand against units, degrees, profiles,
# grants and papers.
MERGES = [
    ('gcgibso@emory.edu', 'greg.gibson@biology.gatech.edu',
     'same NIH award at the same amount, and six PMIDs in common'),
    ('carees@emory.edu', 'chris.rees@emory.edu', 'same NIH award at the same amount'),
    ('psantan@emory.edu', 'phil.santangelo@emory.edu', 'the same three NIH awards at the same amount'),
    ('drenna.waldrop@emory.edu', 'b.a.dwaldr2@emory.edu',
     'profile names her joint Nursing and Rollins appointment; the Rollins record is the other half'),
    ('Cederic Pimentel-Farias', 'cpiment@emory.edu',
     'same neurologist: the Emory Healthcare profile is cederic-manuel-pimentel-farias'),
    ('demetria.joy.smith-graziani@emory.edu', 'djsmit6@emory.edu',
     'same medical oncologist, MD MPH, under her double surname'),
    ('Prabhumallikarjun Patil', 'pspatil@emory.edu',
     'the other record is the same name cut off at fifteen letters'),
    ('wwuest@emory.edu', 'william.wuest@emory.edu', 'Bill Wuest, chemist, under his formal and short name'),
    ('pzhesun@emory.edu', 'phil.sun@emory.edu',
     'profile: directs the imaging centre at the primate research centre, where the other record sits'),
    ('kbusbyi@emory.edu', 'kenneth.busbyiii@choa.org',
     'the CHOA address is Kenneth Busby III; both publish on paediatric integrative medicine'),
    ('william.cash@choa.org', 'wtcash@emory.edu',
     'CHOA profile is william-thomas-cash; both in paediatric haematology-oncology'),
]
SOURCE_RANK = ['NCBI PubMed', 'ORCID registry and NCBI PubMed', 'Europe PMC', 'Public ORCID registry',
               'Crossref', 'OpenAlex']


def norm_title(t):
    return re.sub(r'[^0-9a-z]+', '', html.unescape(t or '').lower())


def src_rank(src):
    for k, name in enumerate(SOURCE_RANK):
        if (src or '').startswith(name):
            return k
    return len(SOURCE_RANK) + (0 if src else 1)


def fix_title(t):
    t = t or ''
    t = re.sub(r'&x?feff;', '', t, flags=re.I).replace('﻿', '')
    return html.unescape(t).strip()


def titlecase_name(n):
    small = {'de', 'da', 'van', 'von', 'der', 'den', 'la', 'le', 'del', 'di'}
    out = []
    for i, w in enumerate(n.split()):
        lw = w.lower()
        if i and lw in small:
            out.append(lw)
        else:
            out.append('-'.join(x[:1].upper() + x[1:] for x in lw.split('-')))
    return ' '.join(out)


def clean(D):
    P = D['pis']
    log = collections.defaultdict(list)

    # ---------------- names ----------------
    for p in P:
        w = p['n'].split()
        m = GLUED.match(w[-1]) if w else None
        if m and len(w) >= 2:
            new = ' '.join(w[:-1] + [m.group('base')])
            deg = m.group('deg')
            g = p.get('g') or ''
            if not re.search(r'\b' + re.escape(deg) + r'\b', g, re.I):
                p['g'] = (g + '; ' + deg) if g else deg
            log['names'].append((p['n'], new, 'degree %s was fused to the surname' % deg))
            p['n'] = new
        if p['n'].isupper() and len(p['n']) > 3:
            new = titlecase_name(p['n'])
            log['names'].append((p['n'], new, 'written in capitals'))
            p['n'] = new

    # ---------------- boilerplate bios ----------------
    shared = collections.Counter(p.get('b') for p in P if p.get('b'))
    for p in P:
        b = p.get('b')
        if b and (shared[b] >= 3 or b.startswith(DISCLAIMER)):
            log['bios'].append((p['n'], b[:80], 'shared word for word by %d people' % shared[b]))
            del p['b']

    # ---------------- duplicate people ----------------
    def find(key):
        hits = [i for i, p in enumerate(P) if p.get('e') == key or p['n'] == key]
        if len(hits) != 1:
            raise SystemExit('merge key %r fits %d records; the merge list needs attention' % (key, len(hits)))
        return hits[0]
    remap = list(range(len(P)))
    gone = set()
    for a_key, b_key, why in MERGES:
        done = [p for p in P if b_key in (p.get('email_aliases') or []) or b_key in (p.get('merge_aliases') or [])]
        if done and not [p for p in P if p.get('e') == b_key or p['n'] == b_key]:
            continue                                  # already merged on an earlier run
        a, b = find(a_key), find(b_key)
        if a == b:
            continue                                  # both keys now name the one merged record
        A, B = P[a], P[b]
        # grants: identical sets are one set; one-sided sets move over; anything
        # else would need RePORTER to settle and stops the build
        ga, gb = [t.strip() for t in A.get('gn') or []], [t.strip() for t in B.get('gn') or []]
        if ga and gb:
            if set(ga) != set(gb) or A.get('m') != B.get('m'):
                raise SystemExit('merging %s and %s: their grants differ; settle with RePORTER first'
                                 % (A['n'], B['n']))
        elif gb:
            for k in ('gn', 'm', 'a'):
                if k in B:
                    A[k] = B[k]
        if B.get('e') and B.get('e') != A.get('e'):
            if A.get('e'):
                A.setdefault('email_aliases', [])
                if B['e'] not in A['email_aliases']:
                    A['email_aliases'].append(B['e'])
            else:
                A['e'] = B['e']
        for al in [B['n']] + (B.get('merge_aliases') or []):
            if al != A['n']:
                A.setdefault('merge_aliases', [])
                if al not in A['merge_aliases']:
                    A['merge_aliases'].append(al)
        for k in ('i', 'd'):
            A[k] = list(dict.fromkeys((A.get(k) or []) + (B.get(k) or [])))
        for k in ('g', 'b', 'u', 'status', 'designation', 't'):
            if not A.get(k) and B.get(k):
                A[k] = B[k]
        if A.get('g') and B.get('g') and re.sub(r'\W', '', A['g']).lower() != re.sub(r'\W', '', B['g']).lower():
            log['review'].append((A['n'], B['n'], 'degrees on the two records differ: %r and %r; kept %r'
                                  % (A['g'], B['g'], A['g'])))
        A['p'] = (A.get('p') or []) + (B.get('p') or [])
        # topic vectors: the stronger weight of each term
        wa = dict(zip((A.get('w') or [])[0::2], (A.get('w') or [])[1::2]))
        for t, v in zip((B.get('w') or [])[0::2], (B.get('w') or [])[1::2]):
            wa[t] = max(v, wa.get(t, 0))
        A['w'] = [x for t, v in sorted(wa.items(), key=lambda kv: -kv[1]) for x in (t, v)]
        A['s'] = (A.get('s') or []) + (B.get('s') or [])
        gone.add(b)
        remap[b] = a
        log['people'].append((A['n'], B['n'], why))

    # indices change once the merged-in records leave
    keep = [i for i in range(len(P)) if i not in gone]
    newi = {old: k for k, old in enumerate(keep)}
    to = lambda i: newi[remap[i]]
    merged_into = {remap[b] for b in gone}
    cap = {}
    for b in gone:
        a = remap[b]
        cap[a] = max(cap.get(a, 0), len(P[b].get('s') or []), len(P[a].get('s') or []) - len(P[b].get('s') or []))
    for i, p in enumerate(P):
        if not p.get('s'):
            continue
        # every list is re-pointed at the new indices; only a merged record,
        # which now holds two lists, is re-ranked and held to its old length
        # an entry is [neighbour, weight, shared topic terms]; the whole entry
        # travels, since the evidence panel explains a link from its terms
        best = {}
        order = []
        for e in p['s']:
            j = to(e[0])
            if j not in best:
                order.append(j)
            if j not in best or e[1] > best[j][1]:
                best[j] = [j] + list(e[1:])
        if i in merged_into:
            order = sorted(best, key=lambda j: -best[j][1])[:max(cap[i], 1)]
        p['s'] = [best[j] for j in order]
    P2 = [P[i] for i in keep]
    for k, p in enumerate(P2):
        if p.get('s'):
            p['s'] = [e for e in p['s'] if e[0] != k]
    def remap_edges(edges):
        acc = collections.defaultdict(set)
        for a, b, ks in edges:
            a, b = to(a), to(b)
            if a == b:
                continue
            acc[(min(a, b), max(a, b))] |= set(ks)
        return [[a, b, sorted(v)] for (a, b), v in sorted(acc.items())]
    D['pubs'] = remap_edges(D.get('pubs') or [])
    D['pis'] = P = P2

    # ---------------- papers ----------------
    for p in P:
        recs = []
        for e in p.get('p') or []:
            e = list(e) + [''] * (4 - len(e))
            t = fix_title(e[0])
            if t != e[0]:
                log['papers'].append((p['n'], e[0][:90], 'stray HTML entity removed'))
            e[0] = t
            recs.append(e)
        # best first, so the copy that survives a duplicate is the best one
        order = sorted(range(len(recs)), key=lambda k: (0 if recs[k][2] else 1, src_rank(recs[k][1]), k))
        kept, by_t, by_pm = [], {}, {}
        for k in order:
            e = recs[k]
            nt = norm_title(e[0])
            if nt in by_t:
                keeper = by_t[nt]
                if not keeper[2] and e[2]:
                    keeper[2] = e[2]
                log['papers'].append((p['n'], e[0][:90], 'the same paper was listed twice'))
                continue
            pm = str(e[2]) if e[2] else ''
            if pm and pm in by_pm:
                other = by_pm[pm]
                on = norm_title(other[0])
                if on[:60] == nt[:60]:
                    log['papers'].append((p['n'], e[0][:90], 'the same paper under a second title variant'))
                    continue
                log['papers'].append((p['n'], e[0][:90],
                                      'PMID %s also belongs to %r; link removed from the less-sourced copy'
                                      % (pm, other[0][:60])))
                e[2] = ''
            by_t[nt] = e
            if e[2]:
                by_pm[str(e[2])] = e
            kept.append((k, e))
        kept.sort(key=lambda x: x[0])               # the original, newest-first order
        p['p'] = [e for _, e in kept]

    PN = D.get('pnames') or []
    lists = [{norm_title(e[0]) for e in p.get('p') or []} for p in P]
    fixed = []
    for a, b, ks in D.get('pubs') or []:
        ks2 = [k for k in ks if k < len(PN) and norm_title(PN[k]) in lists[a] and norm_title(PN[k]) in lists[b]]
        for k in set(ks) - set(ks2):
            log['papers'].append((P[a]['n'] + ' / ' + P[b]['n'], (PN[k] if k < len(PN) else '')[:90],
                                  'co-author link named a paper one side does not list'))
        if ks2:
            fixed.append([a, b, ks2])
    D['pubs'] = fixed

    # ---------------- grants ----------------
    for p in P:
        if p.get('gn'):
            new = [t.strip() for t in p['gn']]
            if new != p['gn']:
                log['grants'].append((p['n'], '', 'grant title whitespace trimmed'))
            p['gn'] = list(dict.fromkeys(new))
    titles = sorted({t for p in P for t in p.get('gn') or []})
    tix = {t: i for i, t in enumerate(titles)}
    holders = collections.defaultdict(list)
    for i, p in enumerate(P):
        for t in p.get('gn') or []:
            holders[t].append(i)
    pairs = collections.defaultdict(set)
    for t, ids in holders.items():
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                pairs[(ids[x], ids[y])].add(tix[t])
    before = len(D.get('grants') or [])
    D['grants'] = [[a, b, sorted(v)] for (a, b), v in sorted(pairs.items())]
    D['gnames'] = titles
    log['grants'].append(('', '', 'co-grant links rebuilt from trimmed titles: %d -> %d'
                          % (before, len(D['grants']))))

    # ---------------- unit sizes follow the merges ----------------
    cnt = collections.Counter(d for p in P for d in p.get('d') or [])
    for k, d in enumerate(D.get('depts') or []):
        d['c'] = cnt[k]
    return log


def check_preserved(before, after):
    """Proof that clean() changed only what it says it changes. For every
    person who was not merged, every field outside the ones cleaning is allowed
    to touch must come through byte for byte, and the similarity list must hold
    the same neighbours with the same weights and terms, only re-numbered.
    Returns a list of problems; empty means the check passed."""
    import copy
    ALLOWED = {'n', 'g', 'b', 'p', 'gn', 's'}
    merged = set()
    key = lambda p: p.get('e') or p['n']
    for a_key, b_key, _ in MERGES:
        for p in before['pis']:
            if p.get('e') in (a_key, b_key) or p['n'] in (a_key, b_key):
                merged.add(key(p))
    # a merged record can change its key (a primary with no email takes the
    # other half's), so it is found under every email and name it now carries
    idx_after = {}
    for k, p in enumerate(after['pis']):
        for al in [key(p), p['n']] + (p.get('email_aliases') or []) + (p.get('merge_aliases') or []):
            idx_after.setdefault(al, k)
    old_key = [key(p) for p in before['pis']]
    problems = []
    for i, p in enumerate(before['pis']):
        if key(p) in merged:
            continue
        k = idx_after.get(key(p))
        if k is None:
            problems.append('%s disappeared' % p['n']); continue
        q = after['pis'][k]
        for f in set(p) | set(q):
            if f in ALLOWED:
                continue
            if p.get(f) != q.get(f):
                problems.append('%s: field %r changed' % (p['n'], f))
        was = {}
        for e in p.get('s') or []:
            j = idx_after.get(old_key[e[0]])
            if j is not None and j != k:
                was[j] = max(was.get(j, -1), e[1])
        now = {e[0]: e[1] for e in q.get('s') or []}
        if was != now:
            problems.append('%s: similarity links changed' % p['n'])
        if any(len(e) != 3 for e in q.get('s') or []):
            problems.append('%s: a similarity entry lost its terms' % p['n'])
    return problems


def read_html(path):
    s = open(path, encoding='utf-8').read()
    i = s.index('<script id="atlasdata"')
    i = s.index('>', i) + 1
    j = s.index('</script>', i)
    return s, i, j, json.loads(s[i:j])


def write_log(log, folder):
    os.makedirs(folder, exist_ok=True)
    heads = {'names': ['before', 'after', 'why'], 'bios': ['person', 'text', 'why'],
             'people': ['kept', 'merged in', 'evidence'], 'papers': ['person', 'title', 'change'],
             'grants': ['person', 'title', 'change'], 'review': ['record a', 'record b', 'note']}
    for k, rows in log.items():
        with open(os.path.join(folder, 'cleaned_%s.csv' % k), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(heads.get(k, ['a', 'b', 'c']))
            w.writerows(rows)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 2:
        print(__doc__); return 2
    s, i, j, D = read_html(a[0])
    before = json.loads(s[i:j])
    log = clean(D)
    bad = check_preserved(before, D)
    if bad:
        print('STOPPED: cleaning changed more than it should have:')
        for b in bad[:20]:
            print('  ', b)
        return 1
    body = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    open(a[1], 'w', encoding='utf-8').write(s[:i] + body + s[j:])
    for k, rows in log.items():
        print('  %-7s %5d' % (k, len(rows)))
    if '--log' in sys.argv:
        write_log(log, sys.argv[sys.argv.index('--log') + 1])
    return 0


if __name__ == '__main__':
    sys.exit(main())
