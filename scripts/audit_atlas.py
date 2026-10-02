#!/usr/bin/env python3
"""
Audit the data inside an Emory Lab Atlas HTML file for errors that can be
proven from the file alone, with no network.

    python3 audit_atlas.py Emory_Lab_Atlas_v78.html            # report
    python3 audit_atlas.py Emory_Lab_Atlas_v78.html --out audit # report + CSVs

Every check is a statement about the data that is either true or false, so the
report is a list of counts, and the exit status is 1 when any check classed as
an error fails. A check that can only raise a question (two people sharing a
surname and several papers, say) is classed as "review" and never fails the run:
the file cannot tell a namesake from a co-author, and the report says so rather
than guessing.

Standard library only.
"""
import collections
import csv
import html
import json
import os
import re
import sys

TRUNC = 110            # the length the old grant scrape cut titles at


def load(path):
    s = open(path, encoding='utf-8').read()
    i = s.index('<script id="atlasdata"')
    i = s.index('>', i) + 1
    j = s.index('</script>', i)
    return json.loads(s[i:j])


def norm_title(t):
    """Two listings of one paper differ in case, hyphens, spacing and a closing
    full stop, so identity is taken on letters and digits alone."""
    return re.sub(r'[^0-9a-z]+', '', html.unescape(t or '').lower())


def name_key(n):
    w = re.sub(r"[^A-Za-z \-']", '', n or '').split()
    return (w[-1].lower(), w[0][0].lower()) if len(w) >= 2 else None


def audit(D):
    P = D['pis']
    G = D.get('gnames') or []
    PN = D.get('pnames') or []
    checks = []          # (id, level, title, count, rows)

    def add(cid, level, title, rows, header):
        checks.append({'id': cid, 'level': level, 'title': title,
                       'count': len(rows), 'header': header, 'rows': rows})

    has = lambda p, k: k in p and p[k] not in (None, [], '', 0)
    nih = D.get('nih') or {}
    verified = bool(nih.get('verified'))

    # ---------------- NIH grants ----------------
    rows = [(p['n'], p.get('a'), len(p['gn']), p.get('m'))
            for p in P if has(p, 'gn') and p.get('a') != len(p['gn'])]
    add('N1', 'error', 'grant count (a) differs from the number of grant titles listed', rows,
        ['person', 'a', 'titles', 'm'])

    rows = [(p['n'], p.get('m')) for p in P if has(p, 'm') and not has(p, 'gn')]
    add('N2', 'error', 'NIH dollars with no grant listed', rows, ['person', 'm'])
    rows = [(p['n'], '; '.join(p['gn'])) for p in P if has(p, 'gn') and not has(p, 'm')]
    add('N3', 'error', 'grants listed with no NIH dollars', rows, ['person', 'titles'])

    rows = [(p['n'], t) for p in P for t in (p.get('gn') or []) if t != t.strip()]
    add('N4', 'error', 'grant title carries stray whitespace', rows, ['person', 'title'])

    rows = [(p['n'], t) for p in P for t in (p.get('gn') or []) if len(t.rstrip()) >= TRUNC - 1
            and not verified]
    add('N5', 'error', 'grant title cut off at %d characters' % TRUNC, rows, ['person', 'title'])

    # the same award credited at different dollar figures to people for whom it
    # is the only award: under any reading of "active NIH funding" those
    # figures have to agree
    single = collections.defaultdict(list)
    for p in P:
        if has(p, 'gn') and len(p['gn']) == 1 and has(p, 'm'):
            single[p['gn'][0].strip()].append((p['n'], p['m']))
    rows = []
    for t, hs in single.items():
        if len({m for _, m in hs}) > 1:
            rows.append((t, '; '.join('%s=%s' % h for h in hs)))
    add('N6', 'error', 'one award credited at different amounts to different people', rows,
        ['title', 'people and amounts'])

    gs = set(G)
    rows = []
    for a, b, ks in D.get('grants') or []:
        for k in ks:
            t = G[k] if k < len(G) else None
            if t is None or t not in (P[a].get('gn') or []) or t not in (P[b].get('gn') or []):
                rows.append((P[a]['n'], P[b]['n'], t))
    add('N7', 'error', 'co-grant link names an award one side does not hold', rows,
        ['person a', 'person b', 'title'])

    # once the verified layer is in, the file has to prove its own arithmetic:
    # a person's figure is the sum of their awards, their count is how many
    # there are, and the headline is those awards each counted once
    rows = []
    if verified:
        whole, parts = {}, {}
        for p in P:
            gx = p.get('gx') or []
            if (p.get('m') or 0) != sum(g[2] for g in gx) or (p.get('a') or 0) != len(gx) \
               or len(p.get('gn') or []) != len(gx):
                rows.append((p['n'], p.get('m'), sum(g[2] for g in gx), p.get('a'), len(gx)))
            for g in gx:
                if g[4] == 'PI':
                    whole[g[1]] = g[2]
                else:
                    for cid, amt in g[6]:
                        parts.setdefault(g[1], {})[cid] = amt
        recomputed = sum(whole.values()) + sum(sum(v.values()) for c, v in parts.items() if c not in whole)
        if recomputed != nih.get('distinct_total'):
            rows.append(('headline', nih.get('distinct_total'), recomputed, '', ''))
    add('N9', 'error', 'verified NIH figures do not add up', rows,
        ['person', 'm', 'sum of awards', 'a', 'awards listed'])

    per_person = sum((p.get('m') or 0) for p in P)
    shared = collections.defaultdict(set)
    for i, p in enumerate(P):
        for t in p.get('gn') or []:
            shared[t.strip()].add(i)
    multi = {t: v for t, v in shared.items() if len(v) > 1}
    rows = [(t, len(v), '; '.join(P[i]['n'] for i in sorted(v))) for t, v in sorted(multi.items())]
    # this one is about the headline, not a row: summing per person counts a
    # multi-PI award once for every PI on it
    level = 'info' if nih.get('distinct_total') is not None else 'error'
    add('N8', level, 'awards held by more than one person (counted once per PI if summed per person)',
        rows, ['title', 'holders', 'people'])

    # ---------------- publications ----------------
    rows = []
    rows_pm = []
    for p in P:
        seen, seenp = {}, {}
        for e in p.get('p') or []:
            k = norm_title(e[0])
            if k in seen:
                rows.append((p['n'], seen[k][0], e[0]))
            else:
                seen[k] = e
            pm = str(e[2]) if len(e) > 2 and e[2] else ''
            if pm:
                if pm in seenp and norm_title(seenp[pm][0]) != k:
                    rows_pm.append((p['n'], pm, seenp[pm][0], e[0]))
                seenp.setdefault(pm, e)
    add('P1', 'error', 'the same paper listed twice for one person', rows, ['person', 'kept', 'duplicate'])
    add('P2', 'error', 'one PMID under two different titles for one person', rows_pm,
        ['person', 'pmid', 'title a', 'title b'])

    rows = [(p['n'], e[0]) for p in P for e in p.get('p') or []
            if re.search(r'&(?:[a-z]+|#\d+);|</?[a-z]+[ >/]', e[0] or '')]
    add('P3', 'error', 'publication title carries HTML markup or entities', rows, ['person', 'title'])

    rows = []
    for a, b, ks in D.get('pubs') or []:
        la = {norm_title(e[0]) for e in P[a].get('p') or []}
        lb = {norm_title(e[0]) for e in P[b].get('p') or []}
        for k in ks:
            t = PN[k] if k < len(PN) else ''
            n = norm_title(t)
            if n not in la or n not in lb:
                rows.append((P[a]['n'], P[b]['n'], t))
    add('P4', 'error', 'co-author link names a paper one side does not list', rows,
        ['person a', 'person b', 'title'])

    pm2 = collections.defaultdict(set)
    for i, p in enumerate(P):
        for e in p.get('p') or []:
            if len(e) > 2 and e[2]:
                pm2[str(e[2])].add(i)
    pair = collections.Counter()
    for ids in pm2.values():
        ids = sorted(ids)
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                kx, ky = name_key(P[ids[x]]['n']), name_key(P[ids[y]]['n'])
                if kx and kx == ky:
                    pair[(ids[x], ids[y])] += 1
    rows = [(P[a]['n'], P[b]['n'], c) for (a, b), c in pair.most_common()]
    add('R1', 'review', 'two people with the same surname and first initial share PMIDs '
        '(one person entered twice, or papers credited to a namesake)', rows,
        ['person a', 'person b', 'shared PMIDs'])

    # ---------------- names and descriptions ----------------
    deg = r'(AB|BA|BS|BSc|BE|JD|DVM|EdD|ScM|MB|MBA|MPA|MPH|MS|MSc|MA|PhD|MD|DO|RN|DrPH|MSN|DNP|PharmD|DDS|DMD)'
    rows = [(p['n'],) for p in P if re.search(r'[a-z]' + deg + r'$', p['n'])]
    add('A1', 'error', 'a degree fused onto the surname', rows, ['person'])
    rows = [(p['n'],) for p in P if p['n'].isupper() and len(p['n']) > 3]
    add('A2', 'error', 'name written entirely in capitals', rows, ['person'])
    rows = [(p['n'], p.get('e', '')) for p in P
            if len(re.sub(r'^\(no\s*first\s*name\)\s*', '', p['n'], flags=re.I).split()) < 2]
    add('R2', 'review', 'a name with no surname', rows, ['person', 'email'])
    shared_b = collections.Counter(p.get('b') for p in P if p.get('b'))
    rows = [(p['n'], p['b'][:80]) for p in P if p.get('b') and shared_b[p['b']] >= 3]
    add('B1', 'error', 'a description shared word for word by several people (site boilerplate)', rows,
        ['person', 'text'])

    # ---------------- emails and roster ----------------
    em = [(p['n'], p['e']) for p in P if p.get('e')]
    rows = [r for r in em if not re.fullmatch(r"[A-Za-z0-9._%+'\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", r[1])]
    add('E1', 'error', 'malformed email address', rows, ['person', 'email'])
    c = collections.Counter(e.lower() for _, e in em)
    rows = [r for r in em if c[r[1].lower()] > 1]
    add('E2', 'error', 'one email address on two people', rows, ['person', 'email'])

    g = D.get('gdbbs') or {}
    progs = set(g.get('programs') or [])
    rows = [(k, ','.join(v.get('p', []))) for k, v in (g.get('people') or {}).items()
            if any(x not in progs for x in v.get('p', []))]
    add('G1', 'error', 'GDBBS entry names a programme that does not exist', rows, ['name', 'programmes'])

    summary = {
        'people': len(P),
        'nih_per_person_sum': per_person,
        'nih_verified': verified,
        'nih_distinct_total': nih.get('distinct_total'),
        'errors': sum(c['count'] for c in checks if c['level'] == 'error'),
        'review': sum(c['count'] for c in checks if c['level'] == 'review'),
    }
    return summary, checks


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print(__doc__)
        return 2
    out = None
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    D = load(args[0])
    summary, checks = audit(D)
    print('Emory Lab Atlas data audit:', os.path.basename(args[0]))
    print('  %d people, NIH summed per person $%s, verified against RePORTER: %s'
          % (summary['people'], format(summary['nih_per_person_sum'], ','), summary['nih_verified']))
    for c in checks:
        mark = 'ok ' if c['count'] == 0 else ('ERR' if c['level'] == 'error' else c['level'][:3].upper())
        print('  [%s] %-3s %5d  %s' % (mark, c['id'], c['count'], c['title']))
    print('  errors: %d   for review: %d' % (summary['errors'], summary['review']))
    if out:
        os.makedirs(out, exist_ok=True)
        for c in checks:
            if not c['rows']:
                continue
            with open(os.path.join(out, c['id'] + '.csv'), 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(c['header'])
                w.writerows(c['rows'])
        with open(os.path.join(out, 'summary.json'), 'w', encoding='utf-8') as f:
            json.dump({'summary': summary,
                       'checks': [{k: v for k, v in c.items() if k != 'rows'} for c in checks]}, f, indent=1)
        print('  written to', out)
    return 1 if summary['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
