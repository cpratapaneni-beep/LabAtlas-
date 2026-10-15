#!/usr/bin/env python3
"""
Rebuild the atlas's NIH layer from NIH RePORTER, and prove it.

    python nih_reporter_verify.py Emory_Lab_Atlas_v78.html            # fetch, match, report
    python nih_reporter_verify.py Emory_Lab_Atlas_v78.html --patch    # ...and write a patched atlas
    python nih_reporter_verify.py --selftest                          # offline proof of the logic

What it fetches
    Every project RePORTER holds for an Emory or CHOA organisation in the
    current and previous NIH fiscal years, from api.reporter.nih.gov/v2. A
    project is one core project number (R01AI123456); each fiscal year is a
    separate record with its own award, supplements are separate records, and
    the components of a centre grant (cores, projects) are records with a
    subproject id under the parent.

What "active NIH funding" means here, and why
    For each core project, the most recent fiscal year on file is its current
    budget year. The award is the sum of the parent-level records for that year
    (the base award plus any supplements). A project is active if its project
    end date is today or later. Those are RePORTER's own fields, used as they
    stand.

    A person's figure is the full award of every active project they are a
    named PI on - the same convention RePORTER uses, so it can be checked on
    the project page. Someone named only on a component is credited that
    component's amount, not the whole centre grant. The institution's total
    counts every award exactly once, which is the number the atlas headline
    shows; summing people instead would count a multi-PI award once per PI.

How people are matched
    RePORTER gives PI names and a stable profile id, not emails. A PI is tied
    to an atlas person on surname and first name, then on surname and first
    initial where that is unique and compatible. A name that fits two atlas
    people is not guessed at, and a profile id whose records would land on two
    different people is dropped. Every one of those cases is written out.

What makes it trustworthy
    The run stops, rather than carrying on with bad numbers, if the API's
    response is missing a field this depends on, if a page comes back short of
    the total the API says it holds, or if a query would pass RePORTER's
    15,000-record paging limit. --selftest runs the whole pipeline against
    built-in records with known answers.

Standard library only; works the same on Windows, macOS and Linux.
"""
import argparse
import collections
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

API = 'https://api.reporter.nih.gov/v2/projects/search'
PAGE = 500                # the API's maximum page size
MAX_OFFSET = 14999        # the API refuses offsets past this
ORG_QUERIES = ['EMORY', "CHILDREN'S HEALTHCARE OF ATLANTA"]
ORG_KEEP = re.compile(r"EMORY|CHILDREN'?S HEALTHCARE OF ATLANTA", re.I)
REQUIRED = ['appl_id', 'fiscal_year', 'core_project_num', 'project_title', 'award_amount',
            'principal_investigators', 'project_end_date', 'organization', 'subproject_id']
FIELDS = REQUIRED + ['project_num', 'project_start_date', 'is_active', 'agency_ic_admin',
                     'activity_code', 'contact_pi_name', 'budget_start', 'budget_end']
TITLE_LIMIT = None        # titles are kept whole; the old scrape cut them at 110


class StopRun(Exception):
    """Raised for anything that would make the output wrong. Never caught
    silently: the run ends and says why."""


# ------------------------------------------------------------------ fetching
def post(body, tries=6):
    data = json.dumps(body).encode('utf-8')
    wait = 2.0
    for attempt in range(tries):
        req = urllib.request.Request(API, data=data, method='POST',
                                     headers={'Content-Type': 'application/json',
                                              'Accept': 'application/json',
                                              'User-Agent': 'emory-lab-atlas-verifier/1'})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(wait); wait *= 2; continue
            raise StopRun('RePORTER answered HTTP %s: %s' % (e.code, e.read()[:300]))
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < tries - 1:
                time.sleep(wait); wait *= 2; continue
            raise StopRun('could not reach RePORTER: %s' % e)
    raise StopRun('RePORTER did not answer after %d tries' % tries)


def check_schema(rec):
    missing = [k for k in REQUIRED if k not in rec]
    if missing:
        raise StopRun('RePORTER records are missing %s; fields present: %s. The API has changed '
                      'shape, and carrying on would produce wrong figures.' % (missing, sorted(rec)))
    pi = (rec.get('principal_investigators') or [{}])[0]
    for k in ('first_name', 'last_name'):
        if pi and k not in pi:
            raise StopRun('PI records are missing %r; fields present: %s' % (k, sorted(pi)))


def fetch_all(fiscal_years, log=print, poster=None, sleep=1.1):
    """Every record for every org query in each fiscal year, with the count
    reconciled against the API's own total for every query."""
    poster = poster or post          # looked up at call time, not bound at definition
    out = {}
    opts = {'fields': True, 'sort': True}
    for fy in fiscal_years:
        for org in ORG_QUERIES:
            crit = {'org_names': [org], 'fiscal_years': [fy]}
            offset, total, ids = 0, None, set()
            while True:
                body = {'criteria': crit, 'offset': offset, 'limit': PAGE}
                if opts['fields']:
                    body['include_fields'] = [_camel(f) for f in FIELDS]
                if opts['sort']:
                    body['sort_field'] = 'appl_id'; body['sort_order'] = 'asc'
                try:
                    res = poster(body)
                except StopRun as e:
                    # an older or newer API may refuse the sort key or a field
                    # name; ask again with less rather than give up
                    if offset == 0 and opts['sort'] and 'HTTP 400' in str(e):
                        opts['sort'] = False; log('  (the API refused the sort key; paging unsorted)'); continue
                    if offset == 0 and opts['fields'] and 'HTTP 400' in str(e):
                        opts['fields'] = False; log('  (the API refused the field list; asking for every field)'); continue
                    raise
                meta = res.get('meta') or {}
                if total is None:
                    total = int(meta.get('total') or 0)
                    if total > MAX_OFFSET + PAGE:
                        raise StopRun('%s FY%s holds %d records, past what RePORTER will page through; '
                                      'the query needs splitting' % (org, fy, total))
                rows = res.get('results') or []
                for rec in rows:
                    try:
                        check_schema(rec)
                    except StopRun:
                        if opts['fields']:
                            # the trimmed field list did not bring back what is
                            # needed; start this query again asking for everything
                            opts['fields'] = False
                            log('  (the field list came back incomplete; asking for every field)')
                            offset, total, ids = -PAGE, None, set()
                            break
                        raise
                    out[rec['appl_id']] = rec
                    ids.add(rec['appl_id'])
                offset += PAGE
                if offset > 0 and (not rows or offset >= total):
                    break
                time.sleep(sleep)
            if len(ids) != total:
                raise StopRun('%s FY%s: RePORTER reported %d records but %d distinct ones came back '
                              '(a page was short or repeated)' % (org, fy, total, len(ids)))
            log('  FY%s  %-34s %5d records' % (fy, org, total))
            time.sleep(sleep)
    return list(out.values())


def _camel(f):
    # the API accepts include_fields in PascalCase and returns snake_case
    return ''.join(w.capitalize() for w in f.split('_'))


# ------------------------------------------------------------------ names
SUFFIX = {'jr', 'sr', 'ii', 'iii', 'iv', 'md', 'phd', 'mph', 'dr'}
NICK = {'bill': 'william', 'will': 'william', 'bob': 'robert', 'rob': 'robert', 'jim': 'james',
        'jimmy': 'james', 'mike': 'michael', 'tom': 'thomas', 'dan': 'daniel', 'dave': 'david',
        'chris': 'christopher', 'kate': 'katherine', 'katie': 'katherine', 'liz': 'elizabeth',
        'beth': 'elizabeth', 'joe': 'joseph', 'steve': 'stephen', 'greg': 'gregory',
        'tony': 'anthony', 'andy': 'andrew', 'rick': 'richard', 'dick': 'richard',
        'ted': 'edward', 'ed': 'edward', 'jeff': 'jeffrey', 'matt': 'matthew', 'nick': 'nicholas',
        'sam': 'samuel', 'ben': 'benjamin', 'alex': 'alexander', 'jen': 'jennifer',
        'jenny': 'jennifer', 'sue': 'susan', 'pat': 'patricia', 'peggy': 'margaret',
        'meg': 'margaret', 'jon': 'jonathan', 'nate': 'nathan', 'zeke': 'ezequiel'}


def fold(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def split_atlas_name(n):
    """'Mary-Ann O'Neil Jr.' -> ('mary-ann', "oneil")"""
    n = re.sub(r'^\(no\s*first\s*name\)\s*', '', n or '', flags=re.I)
    n = re.sub(r'\([^)]*\)', ' ', n)            # "William (Bill) Stokes" -> "William Stokes"
    w = [x for x in re.split(r'[\s,]+', fold(n).replace('.', ' ')) if x]
    w = [x for x in w if x not in SUFFIX]
    w = [re.sub(r"[^a-z\-]", '', x) for x in w]
    w = [x for x in w if x]
    if len(w) < 2:
        return None
    return w[0], w[-1]


def canon_first(f):
    f = re.sub(r'[^a-z]', '', f)
    return NICK.get(f, f)


def compatible(a, b):
    a, b = canon_first(a), canon_first(b)
    return bool(a and b) and (a == b or a.startswith(b) or b.startswith(a))


class Matcher:
    def __init__(self, people):
        self.people = people
        # whole surnames and fragments of hyphenated ones are kept apart: a
        # fragment is only consulted when no whole surname fits, so a real
        # "Stephanie Brown" is not made ambiguous by a "Stephanie Brown-Johnson",
        # and a two-letter particle like "al" is never an index key at all
        self.full = collections.defaultdict(set)
        self.initial = collections.defaultdict(set)
        self.part = collections.defaultdict(set)
        for i, p in enumerate(people):
            k = split_atlas_name(p['n'])
            if not k:
                continue
            first, last = k
            for ln in {last, last.replace('-', '')}:
                self.full[(ln, canon_first(first))].add(i)
                self.initial[(ln, first[:1])].add(i)
            if '-' in last:
                for frag in last.split('-'):
                    if len(frag) >= 3:
                        self.part[(frag, canon_first(first))].add(i)

    def match(self, pi, title=None):
        aid, why = self._match(pi)
        if aid is None and why.startswith('fits') and title:
            # Two atlas people share this name. If exactly one of them already
            # lists this award (the old scrape kept titles, cut at 110
            # characters), that settles it; otherwise it stays unmatched.
            ids = self.candidates(pi)
            t = re.sub(r'[^0-9a-z]+', '', fold(title))
            hit = [i for i in ids
                   if any((lambda o: o and (t.startswith(o) or o.startswith(t)))(re.sub(r'[^0-9a-z]+', '', fold(g)))
                          for g in self.people[i].get('gn') or [])]
            if len(hit) == 1:
                return hit[0], 'name fits %d people; settled by the award already on their record' % len(ids)
        return aid, why

    def candidates(self, pi):
        first = canon_first(fold(pi.get('first_name') or '').split(' ')[0])
        last = re.sub(r"[^a-z\-]", '', fold(pi.get('last_name') or '').replace(' ', '-'))
        out = set()
        for ln in (last, last.replace('-', '')):
            out |= self.full.get((ln, first)) or set()
        if not out:
            out = {i for i in (self.initial.get((last, first[:1])) or set())
                   if compatible(split_atlas_name(self.people[i]['n'])[0], first)}
        return out

    def _match(self, pi):
        first = canon_first(fold(pi.get('first_name') or '').split(' ')[0])
        last = re.sub(r"[^a-z\-]", '', fold(pi.get('last_name') or '').replace(' ', '-'))
        if not first or not last:
            return None, 'no name'
        for ln in (last, last.replace('-', '')):
            ids = self.full.get((ln, first))
            if ids:
                if len(ids) == 1:
                    return next(iter(ids)), 'surname and first name'
                return None, 'fits %d atlas people' % len(ids)
        ids = self.initial.get((last, first[:1])) or set()
        ids = {i for i in ids if compatible(split_atlas_name(self.people[i]['n'])[0], first)}
        if len(ids) == 1:
            return next(iter(ids)), 'surname and compatible first name'
        if len(ids) > 1:
            return None, 'fits %d atlas people' % len(ids)
        # RePORTER "WALDROP" for an atlas "Drenna Waldrop-Valverde"
        ids = self.part.get((last, first)) or set()
        if len(ids) == 1:
            return next(iter(ids)), 'part of an atlas double surname and first name'
        if len(ids) > 1:
            return None, 'fits %d atlas people' % len(ids)
        # "GARCIA LOPEZ" against an atlas "Maria Garcia Lopez": each part of a
        # multi-part surname, but only on an exact first name and a unique fit
        if '-' in last:
            hits = set()
            for part in last.split('-'):
                hits |= self.full.get((part, first)) or set()
            if len(hits) == 1:
                return next(iter(hits)), 'part of a multi-part surname and first name'
            if len(hits) > 1:
                return None, 'fits %d atlas people' % len(hits)
        return None, 'no atlas person by that name'


# ------------------------------------------------------------------ the model
def build(records, people, today):
    """Turns RePORTER records into per-project awards and per-person figures.
    Pure function of its inputs, so --selftest can check it exactly."""
    orgs = collections.Counter((r.get('organization') or {}).get('org_name') or '' for r in records)
    kept = [r for r in records if ORG_KEEP.search((r.get('organization') or {}).get('org_name') or '')]
    dropped_orgs = {o: c for o, c in orgs.items() if not ORG_KEEP.search(o)}

    by_core = collections.defaultdict(list)
    for r in kept:
        core = r.get('core_project_num') or r.get('project_num') or str(r['appl_id'])
        by_core[core].append(r)

    projects = []
    for core, rs in by_core.items():
        fy = max(r['fiscal_year'] for r in rs)
        cur = [r for r in rs if r['fiscal_year'] == fy]
        parents = [r for r in cur if not r.get('subproject_id')]
        comps = [r for r in cur if r.get('subproject_id')]
        end = max((r.get('project_end_date') or '')[:10] for r in cur)
        active = bool(end) and end >= today
        base = parents[0] if parents else cur[0]
        amount = sum(int(r.get('award_amount') or 0) for r in parents)
        pis = {}
        for r in parents:
            for pi in r.get('principal_investigators') or []:
                key = pi.get('profile_id') or (pi.get('last_name'), pi.get('first_name'))
                cur_pi = pis.setdefault(key, dict(pi, role='PI'))
                cur_pi['is_contact_pi'] = bool(cur_pi.get('is_contact_pi') or pi.get('is_contact_pi'))
        components = []
        for r in comps:
            cp = []
            for pi in r.get('principal_investigators') or []:
                key = pi.get('profile_id') or (pi.get('last_name'), pi.get('first_name'))
                if key not in pis:
                    cp.append(dict(pi, role='component'))
            components.append({'appl_id': r['appl_id'], 'subproject_id': r.get('subproject_id'),
                               'title': (r.get('project_title') or '').strip(),
                               'amount': int(r.get('award_amount') or 0), 'pis': cp})
        comp_sum = sum(c['amount'] for c in components)
        projects.append({
            'core': core, 'appl_id': base['appl_id'], 'fy': fy,
            'title': (base.get('project_title') or '').strip(),
            'amount': amount, 'active': active, 'end': end,
            'activity': base.get('activity_code') or '',
            'ic': ((base.get('agency_ic_admin') or {}).get('abbreviation') or ''),
            'org': (base.get('organization') or {}).get('org_name') or '',
            'supplements': max(0, len(parents) - 1),
            'pis': list(pis.values()), 'components': components,
            'component_sum': comp_sum,
            'only_components': not parents,
        })

    m = Matcher(people)
    # pass 1: where does each RePORTER profile land?
    lands = collections.defaultdict(set)
    for pr in projects:
        if not pr['active']:
            continue
        for pi, t in [(x, pr['title']) for x in pr['pis']] + [(x, c['title']) for c in pr['components'] for x in c['pis']]:
            aid, _ = m.match(pi, t)
            if aid is not None and pi.get('profile_id') is not None:
                lands[pi['profile_id']].add(aid)
    clash = {pid for pid, s_ in lands.items() if len(s_) > 1}
    conflicts = [{'profile_id': pid, 'atlas': sorted(people[a]['n'] for a in lands[pid])} for pid in sorted(clash)]
    # pass 2: attribute
    unmatched = []
    per = collections.defaultdict(lambda: {'m': 0, 'grants': []})
    for pr in projects:
        if not pr['active']:
            continue
        credit = {}                                   # atlas id -> (amount, title, role, pi)
        for pi in pr['pis']:
            aid, why = m.match(pi, pr['title'])
            if pi.get('profile_id') in clash:
                aid, why = None, 'RePORTER profile matches two atlas people'
            if aid is None:
                unmatched.append({'name': ' '.join(filter(None, [pi.get('first_name'), pi.get('middle_name'), pi.get('last_name')])),
                                  'profile_id': pi.get('profile_id'), 'reason': why, 'core': pr['core'],
                                  'title': pr['title'], 'amount': pr['amount']})
                continue
            credit[aid] = [pr['amount'], pr['title'], 'PI', pi, why, []]
        for c in pr['components']:
            for pi in c['pis']:
                aid, why = m.match(pi, c['title'])
                if pi.get('profile_id') in clash:
                    aid, why = None, 'RePORTER profile matches two atlas people'
                if aid is None:
                    unmatched.append({'name': ' '.join(filter(None, [pi.get('first_name'), pi.get('middle_name'), pi.get('last_name')])),
                                      'profile_id': pi.get('profile_id'), 'reason': why, 'core': pr['core'],
                                      'title': c['title'], 'amount': c['amount']})
                    continue
                if aid in credit and credit[aid][2] == 'PI':
                    continue                          # already credited the whole award
                if aid in credit:                     # a second component of the same centre
                    if c['appl_id'] not in [x[0] for x in credit[aid][5]]:
                        credit[aid][0] += c['amount']
                        credit[aid][5].append([c['appl_id'], c['amount']])
                else:
                    credit[aid] = [c['amount'], c['title'], 'component', pi, why, [[c['appl_id'], c['amount']]]]
        for aid, (amt, title, role, pi, why, comps) in credit.items():
            per[aid]['m'] += amt
            per[aid]['grants'].append({'title': title, 'core': pr['core'], 'appl_id': pr['appl_id'],
                                       'amount': amt, 'fy': pr['fy'], 'role': role,
                                       'contact': bool(pi.get('is_contact_pi')),
                                       'n_pis': len(pr['pis']), 'match': why, 'comps': comps})

    # Two institutional figures. The atlas headline is about the atlas's own
    # investigators, so it counts each award that at least one of them holds,
    # once: the whole award where one of them is a PI on it, and only the
    # components they lead where that is all they hold. The Emory-wide figure,
    # every active award whoever holds it, is reported alongside for context.
    active = [p for p in projects if p['active']]
    by_core = {p['core']: p for p in active}
    held = collections.defaultdict(lambda: {'whole': False, 'parts': 0})
    for aid, v in per.items():
        for g in v['grants']:
            h = held[g['core']]
            if g['role'] == 'PI':
                h['whole'] = True
            else:
                h['parts'] += g['amount']
    distinct_total = 0
    for core, h in held.items():
        pr = by_core[core]
        if h['whole']:
            distinct_total += pr['amount']
        else:
            # components can be shared by two atlas people; count each once
            led = {}
            for aid, v in per.items():
                for g in v['grants']:
                    if g['core'] == core:
                        for cid, camt in g['comps']:
                            led[cid] = camt
            distinct_total += sum(led.values())
    emory_total = sum(p['amount'] for p in active if not p['only_components'])
    emory_total += sum(c['amount'] for p in active if p['only_components'] for c in p['components'])
    return {
        'projects': projects, 'people': per, 'unmatched': unmatched, 'conflicts': conflicts,
        'orgs_kept': {o: c for o, c in orgs.items() if o not in dropped_orgs},
        'orgs_dropped': dropped_orgs,
        'distinct_total': distinct_total, 'emory_total': emory_total,
        'per_person_sum': sum(v['m'] for v in per.values()),
        'active_projects': len(active),
    }


# ------------------------------------------------------------------ atlas I/O
def read_atlas(path):
    s = open(path, encoding='utf-8').read()
    i = s.index('<script id="atlasdata"')
    i = s.index('>', i) + 1
    j = s.index('</script>', i)
    return s, i, j, json.loads(s[i:j])


def patch(path, D, R, today, fys, out_path):
    s, i, j, _ = read_atlas(path)
    P = D['pis']
    for p in P:
        for k in ('m', 'a', 'gn', 'gx'):
            p.pop(k, None)
    titles, tix = [], {}
    core_people = collections.defaultdict(set)
    for aid, v in R['people'].items():
        g = sorted(v['grants'], key=lambda x: -x['amount'])
        P[aid]['m'] = v['m']
        P[aid]['a'] = len(g)
        P[aid]['gn'] = [x['title'] for x in g]
        # per-grant evidence, so the profile can link each one to its RePORTER page
        # [appl id, core project, amount, fiscal year, 'PI' or 'component',
        #  PIs on the award, [[component appl id, amount], ...]]
        P[aid]['gx'] = [[x['appl_id'], x['core'], x['amount'], x['fy'], x['role'], x['n_pis'], x['comps']]
                        for x in g]
        for x in g:
            core_people[x['core']].add(aid)
            if x['title'] not in tix:
                tix[x['title']] = len(titles); titles.append(x['title'])
    title_of = {}
    for aid, v in R['people'].items():
        for x in v['grants']:
            title_of.setdefault(x['core'], x['title'])
    pairs = collections.defaultdict(set)
    for core, ids in core_people.items():
        ids = sorted(ids)
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                pairs[(ids[a], ids[b])].add(tix[title_of[core]])
    D['grants'] = [[a, b, sorted(k)] for (a, b), k in sorted(pairs.items())]
    D['gnames'] = titles
    D['nih'] = {'verified': True, 'source': API, 'generated': today, 'fiscal_years': fys,
                'distinct_total': R['distinct_total'], 'per_person_sum': R['per_person_sum'],
                'active_projects': R['active_projects'], 'people': len(R['people'])}
    body = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    open(out_path, 'w', encoding='utf-8').write(s[:i] + body + s[j:])


def current_fy(today):
    d = dt.date.fromisoformat(today)
    return d.year + 1 if d.month >= 10 else d.year


def report(D, R, outdir):
    P = D['pis']
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'nih_changes.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['person', 'email', 'old_m', 'new_m', 'old_a', 'new_a', 'change'])
        for aid, p in enumerate(P):
            nv = R['people'].get(aid)
            om, oa = p.get('m') or 0, p.get('a') or 0
            nm, na = (nv['m'], len(nv['grants'])) if nv else (0, 0)
            if om == nm and oa == na:
                continue
            why = ('new' if not om and nm else 'no active award found' if om and not nm else 'amount or count changed')
            w.writerow([p['n'], p.get('e', ''), om, nm, oa, na, why])
    with open(os.path.join(outdir, 'nih_unmatched.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['RePORTER name', 'profile_id', 'reason', 'core project', 'title', 'amount'])
        for u in R['unmatched']:
            w.writerow([u['name'], u['profile_id'], u['reason'], u['core'], u['title'], u['amount']])
    with open(os.path.join(outdir, 'nih_conflicts.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['profile_id', 'atlas people it would match'])
        for c in R['conflicts']:
            w.writerow([c['profile_id'], '; '.join(c['atlas'])])
    with open(os.path.join(outdir, 'nih_grants.json'), 'w', encoding='utf-8') as f:
        dump = {k: v for k, v in R.items() if k != 'people'}
        dump['people'] = {P[a]['n']: v for a, v in R['people'].items()}
        json.dump(dump, f, indent=1)


# ------------------------------------------------------------------ self-test
def selftest():
    """The whole pipeline, on records whose right answer is known."""
    people = [{'n': 'George R. Painter'}, {'n': 'Richard Plemper'}, {'n': 'Lou Ann Brown'},
              {'n': 'Xin Hu'}, {'n': 'Xin Hu'.replace('Xin', 'Xiao')}, {'n': 'Michael Chung'},
              {'n': 'Michael Chung'.replace('Michael', 'Mikhail')}, {'n': 'William Tyor'},
              {'n': 'Frances Eun-Hyung Lee'}]
    org = {'org_name': 'EMORY UNIVERSITY'}
    def rec(appl, fy, core, title, amt, pis, sub=None, end='2028-06-30', o=org):
        return {'appl_id': appl, 'fiscal_year': fy, 'core_project_num': core, 'project_title': title,
                'award_amount': amt, 'principal_investigators': pis, 'project_end_date': end,
                'organization': o, 'subproject_id': sub, 'activity_code': core[:3],
                'agency_ic_admin': {'abbreviation': 'NIAID'}}
    pi = lambda f, l, pid, c=False, mid='': {'first_name': f, 'middle_name': mid, 'last_name': l,
                                              'profile_id': pid, 'is_contact_pi': c,
                                              'full_name': (f + ' ' + l).upper()}
    R = [
        # one multi-PI centre award, two fiscal years; only the latest counts,
        # and it counts once in the total but in full for each PI
        rec(1, 2025, 'U19AI171403', 'Antiviral drug discovery', 40_000_000,
            [pi('GEORGE', 'PAINTER', 11, True), pi('RICHARD', 'PLEMPER', 12)]),
        rec(2, 2026, 'U19AI171403', 'Antiviral drug discovery', 51_914_880,
            [pi('GEORGE', 'PAINTER', 11, True), pi('RICHARD', 'PLEMPER', 12)]),
        # a supplement in the same year adds to the award
        rec(3, 2026, 'U19AI171403', 'Antiviral drug discovery', 1_000_000,
            [pi('GEORGE', 'PAINTER', 11, True), pi('RICHARD', 'PLEMPER', 12)]),
        # a component of it, led by someone else: credited the component only,
        # and not added to the institutional total a second time
        rec(4, 2026, 'U19AI171403', 'Core B: Chemistry', 46_678,
            [pi('LOU ANN', 'BROWN', 13)], sub='7002'),
        # an ended project is not active
        rec(5, 2026, 'R01AI000001', 'Old study', 500_000, [pi('RICHARD', 'PLEMPER', 12, True)],
            end='2026-01-31'),
        # an ambiguous name is left alone and reported
        rec(6, 2026, 'R01GM000002', 'Unrelated', 300_000, [pi('XIN', 'HU', 14, True)]),
        # a record from another institution is dropped even though it was returned
        rec(7, 2026, 'R01GM000003', 'Elsewhere', 999_999, [pi('WILLIAM', 'TYOR', 15, True)],
            o={'org_name': 'GEORGIA INSTITUTE OF TECHNOLOGY'}),
        # a nickname in the record still reaches the atlas's full first name
        rec(8, 2026, 'R21NS000004', 'Neuro', 200_000, [pi('BILL', 'TYOR', 15, True)]),
        # a hyphenated given name in the atlas, a plain one in RePORTER
        rec(9, 2026, 'R01AI000005', 'Plasma cells', 100_000, [pi('FRANCES', 'LEE', 16, True, 'EUN-HYUNG')]),
        # one person leading two components of the same centre gets both
        rec(10, 2026, 'U19AI171403', 'Core C: Virology', 20_000, [pi('LOU ANN', 'BROWN', 13)], sub='7003'),
        # one RePORTER profile appearing under two names that fit two different
        # atlas people: refused everywhere, not just where the clash shows
        rec(11, 2026, 'R01AI000006', 'Clash a', 70_000, [pi('XIAO', 'HU', 17, True)]),
        rec(12, 2026, 'R01AI000007', 'Clash b', 80_000, [pi('MIKHAIL', 'CHUNG', 17, True)]),
        # a two-part surname written without the hyphen
        rec(13, 2026, 'R01AI000008', 'Two surnames', 90_000, [pi('MARIA', 'GARCIA LOPEZ', 18, True)]),
        # a shared name, settled by the award the old record already lists
        rec(17, 2026, 'R01AI000010', 'Establishing PREMISE: A PrEP Epidemiology, Modeling, and Surveillance System (PREMISE)',
            300_000, [pi('PATRICK', 'SULLIVAN', 22, True)]),
        # the same shared name on an award neither record lists: left alone
        rec(18, 2026, 'R01AI000011', 'Something new', 60_000, [pi('PATRICK', 'SULLIVAN', 22, True)]),
        # a centre whose overall PI is not in the atlas: only the components
        # atlas people lead count, and a component two of them share counts once
        rec(14, 2026, 'P01AG000009', 'Ageing centre', 5_000_000, [pi('ZED', 'OUTSIDER', 19, True)]),
        rec(15, 2026, 'P01AG000009', 'Project 1', 10_000, [pi('ANA', 'RUIZ', 20)], sub='0001'),
        rec(16, 2026, 'P01AG000009', 'Project 2', 15_000, [pi('ANA', 'RUIZ', 20), pi('BEN', 'ORTIZ', 21)], sub='0002'),
    ]
    people.append({'n': 'Patrick Sullivan', 'gn': ['Establishing PREMISE: A PrEP Epidemiology, Modeling, and Surveillance System']})
    people.append({'n': 'Patrick Sullivan'})
    people.append({'n': 'Maria Garcia Lopez'})
    people.append({'n': 'Ana Ruiz'})
    people.append({'n': 'Ben Ortiz'})
    people.append({'n': 'Xin Hu'})         # the second Xin Hu: makes the name ambiguous
    today = '2026-09-25'
    out = build(R, people, today)
    P = out['people']
    ok = True
    def eq(label, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print('  %s %-58s %s' % ('ok ' if good else 'BAD', label, got if good else '%r, wanted %r' % (got, want)))
    eq('Painter credited latest year + supplement', P[0]['m'], 52_914_880)
    eq('Plemper credited the same award in full', P[1]['m'], 52_914_880)
    eq('Plemper not credited the ended project', len(P[1]['grants']), 1)
    eq('component lead credited both components only', P[2]['m'], 46_678 + 20_000)
    eq('institutional total counts each award once', out['distinct_total'],
       52_914_880 + 200_000 + 100_000 + 90_000 + 25_000 + 300_000)
    names = [q['n'] for q in people]
    eq('shared name settled by the award on record', P[names.index('Patrick Sullivan')]['m'], 300_000)
    eq('shared name on an unknown award left alone', any(u['core'] == 'R01AI000011' for u in out['unmatched']), True)
    eq('component lead on two projects', P[names.index('Ana Ruiz')]['m'], 25_000)
    eq('co-lead of one project', P[names.index('Ben Ortiz')]['m'], 15_000)
    eq('per-person sum is larger than the total', out['per_person_sum'] > out['distinct_total'], True)
    eq('ambiguous "Xin Hu" not attributed', any(g['core'] == 'R01GM000002' for v in P.values() for g in v['grants']), False)
    eq('ambiguous name reported', any(u['core'] == 'R01GM000002' for u in out['unmatched']), True)
    eq('other institution dropped', 'GEORGIA INSTITUTE OF TECHNOLOGY' in out['orgs_dropped'], True)
    eq('nickname Bill reaches William Tyor', P[7]['m'], 200_000)
    eq('Frances Lee reached on surname + first name', P[8]['m'], 100_000)
    eq('clashing profile credited to neither person', (P.get(4, {}).get('m', 0), P.get(6, {}).get('m', 0)), (0, 0))
    eq('clash reported', [c['profile_id'] for c in out['conflicts']], [17])
    eq('two-part surname matched', P[[q['n'] for q in people].index('Maria Garcia Lopez')]['m'], 90_000)
    eq('Emory-wide total includes unmatched awards', out['emory_total'],
       53_304_880 + 300_000 + 70_000 + 80_000 + 5_000_000 + 300_000 + 60_000)
    eq('active projects', out['active_projects'], 10)

    # paging: short pages and totals are reconciled, and a short page stops the run
    calls = []
    def fake(body):
        calls.append(body['offset'])
        n = 1203
        start = body['offset']
        return {'meta': {'total': n}, 'results': [dict(R[1], appl_id=10_000 + k) for k in range(start, min(n, start + PAGE))]}
    got = fetch_all([2026], log=lambda *a: None, poster=fake, sleep=0)
    eq('paging reads every record (2 queries x 1203)', len(got), 1203)
    eq('paging offsets', sorted(set(calls)), [0, 500, 1000])
    def short(body):
        return {'meta': {'total': 900}, 'results': [dict(R[1], appl_id=20_000 + body['offset'] + k) for k in range(300)]}
    try:
        fetch_all([2026], log=lambda *a: None, poster=short, sleep=0)
        eq('a short page stops the run', False, True)
    except StopRun:
        eq('a short page stops the run', True, True)
    seen = []
    def picky(body):
        seen.append('sort_field' in body)
        if 'sort_field' in body:
            raise StopRun('RePORTER answered HTTP 400: bad sort field')
        return {'meta': {'total': 2}, 'results': [dict(R[1], appl_id=30_001), dict(R[1], appl_id=30_002)]}
    got = fetch_all([2026], log=lambda *a: None, poster=picky, sleep=0)
    eq('a refused sort key is dropped, not fatal', (len(got), seen[0], seen[-1]), (2, True, False))
    def reshaped(body):
        r = dict(R[1]); r.pop('award_amount')
        return {'meta': {'total': 1}, 'results': [r]}
    try:
        fetch_all([2026], log=lambda *a: None, poster=reshaped, sleep=0)
        eq('a changed API shape stops the run', False, True)
    except StopRun:
        eq('a changed API shape stops the run', True, True)
    print('self-test', 'passed' if ok else 'FAILED')
    return 0 if ok else 1


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('atlas', nargs='?')
    ap.add_argument('--patch', action='store_true', help='write <atlas>_nih.html with the verified layer')
    ap.add_argument('--out', default='nih_verify', help='folder for the reports')
    ap.add_argument('--today', default=dt.date.today().isoformat())
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--min-projects', type=int, default=300,
                    help='refuse to write anything if fewer active projects come back')
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors='replace')    # a Windows console cannot print every name
    except Exception:
        pass
    if a.selftest:
        return selftest()
    if not a.atlas:
        ap.print_help(); return 2
    print('Reading', a.atlas)
    _, _, _, D = read_atlas(a.atlas)
    fy = current_fy(a.today)
    # six fiscal years: a project's latest record can be several years old
    # while it is still active (a multi-year award, or a no-cost extension)
    fys = list(range(fy - 5, fy + 1))
    print('Fetching Emory and CHOA projects from NIH RePORTER, FY%s-FY%s (about a minute)...' % (fys[0], fys[-1]))
    try:
        recs = fetch_all(fys)
        R = build(recs, D['pis'], a.today)
        # Emory holds well over a thousand active NIH awards. A handful means
        # the search went wrong (an organisation name the API no longer
        # recognises, say), and patching with it would wipe the layer.
        if R['active_projects'] < a.min_projects:
            raise StopRun('only %d active projects came back; expected at least %d. Nothing written.'
                          % (R['active_projects'], a.min_projects))
    except StopRun as e:
        print('\nSTOPPED:', e)
        return 1
    print('\nOrganisations kept:')
    for o, c in sorted(R['orgs_kept'].items(), key=lambda x: -x[1]):
        print('  %5d  %s' % (c, o))
    if R['orgs_dropped']:
        print('Returned by the search but not Emory or CHOA, so left out:')
        for o, c in sorted(R['orgs_dropped'].items(), key=lambda x: -x[1])[:15]:
            print('  %5d  %s' % (c, o))
    old = sum((p.get('m') or 0) for p in D['pis'])
    print('\nActive projects:            %d' % R['active_projects'])
    print('Atlas total:                $%s   (awards held by atlas investigators, each once)' % format(R['distinct_total'], ','))
    print('Emory-wide total:           $%s   (every active Emory/CHOA award, for context)' % format(R['emory_total'], ','))
    print('Summed per investigator:    $%s   (a multi-PI award counts once per PI)' % format(R['per_person_sum'], ','))
    print('The atlas had, per person:  $%s' % format(old, ','))
    print('Investigators with an active award: %d   (atlas had %d)'
          % (len(R['people']), sum(1 for p in D['pis'] if p.get('m'))))
    print('PI listings not matched to an atlas person: %d   profile clashes: %d'
          % (len(R['unmatched']), len(R['conflicts'])))
    report(D, R, a.out)
    print('Reports written to', a.out + os.sep)
    if a.patch:
        outp = re.sub(r'\.html$', '', a.atlas) + '_nih.html'
        patch(a.atlas, D, R, a.today, fys, outp)
        print('Patched atlas written to', outp)
    return 0


if __name__ == '__main__':
    sys.exit(main())
