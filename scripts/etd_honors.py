#!/usr/bin/env python3
"""Add Emory College honors-thesis advisors to the atlas's undergraduate mentors.

Emory's theses and dissertations repository (etd.library.emory.edu) holds every
honors thesis Emory College students have deposited. Each record names the
thesis advisor ("Committee Chair / Thesis Advisor"). An advisor of an honors
thesis has taken an undergraduate into their research, so they are marked the
same way the symposium mentors are: a record per thesis (year, term, title,
department, a link to the record) in the page's `surehist` block, which drives
the "Mentored undergrads" mark, the profile's mentoring record and the Past
undergraduate mentors tab.

Students' names are never read into the output: the crawl keeps only the
title, term, school, department, degree, submission type and committee.

Two steps
  crawl   read every record the repository lists in its sitemap (robots.txt
          allows it; the catalog search is closed to scripts, the record pages
          are not). A few requests at a time with a pause, resumable.
  merge   take the honors theses, match each advisor to an atlas investigator
          by name (unique matches only, the symposium script's matcher), and
          write the updated `surehist` block (or splice it into the atlas).

Usage
  python scripts/etd_honors.py crawl --cache build/etd
  python scripts/etd_honors.py merge --atlas Emory_Lab_Atlas_v120.html --cache build/etd \
      --report build/etd/honors_report.md --write-atlas
"""
import argparse, collections, html, json, os, re, sys, threading, queue, time, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from symposium_scrape import Names, read_atlas, tokens  # noqa: E402

ETD = 'https://etd.library.emory.edu'
# the repository turns away clients that do not look like a browser
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
LABELS = {'Rights statement', 'School', 'Department', 'Subfield / Discipline', 'Degree', 'Submission', 'Language',
          'Research Field', 'Keyword', 'Committee Chair / Thesis Advisor', 'Committee Members', '×', 'Partnering Agencies'}


def get(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xml'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410):     # 403 means the site is turning requests away
                raise
            time.sleep(3 * (k + 1))
        except Exception:
            time.sleep(3 * (k + 1))
    raise TimeoutError(url)


def fields(page):
    """The record's metadata, read from its page. No author name is kept."""
    s = re.sub(r'<script.*?</script>|<style.*?</style>', '', page, flags=re.S)
    L = [l.strip() for l in html.unescape(re.sub(r'<[^>]+>', '\n', s)).split('\n') if l.strip()]

    def after(label):
        if label not in L:
            return []
        out = []
        for x in L[L.index(label) + 1:]:
            if x in LABELS:
                break
            out.append(x)
        return out
    m = re.search(r'\(((?:Spring|Summer|Fall|Winter)\s+\d{4})\)', ' '.join(L[:40]))
    # records deposited before about 2018 give only "(YYYY)" after the author, on the line above the
    # permanent URL, and break the title over several lines
    h = L.index('Home') if 'Home' in L else -1
    p = next((k for k in range(h + 1, len(L)) if L[k].startswith('Permanent URL')), None) if h >= 0 else None
    title, year = (L[h + 1] if h >= 0 and h + 1 < len(L) else ''), None
    if p is not None:
        end = p - 2 if L[p - 2] in ('Open Access', 'Restricted', 'Embargoed', 'Campus Only') else p - 1
        title = ' '.join(L[h + 1:end]) or title
        y = re.search(r'\((\d{4})\)\s*$', L[p - 1])
        year = int(y.group(1)) if y else None
    return {'title': title, 'term': m.group(1) if m else '', 'year': year,
            'school': after('School')[:1], 'dept': after('Department')[:2], 'sub': after('Subfield / Discipline')[:2],
            'degree': after('Degree')[:1], 'submission': after('Submission')[:1],
            'chair': after('Committee Chair / Thesis Advisor')[:4], 'members': after('Committee Members')[:8]}


def crawl(a):
    os.makedirs(a.cache, exist_ok=True)
    out = os.path.join(a.cache, 'records.jsonl')
    ids = re.findall(r'<loc>' + re.escape(ETD) + r'/concern/etds/([a-z0-9]+)</loc>', get(ETD + '/sitemap.xml'))
    done = set()
    if os.path.exists(out):
        for l in open(out):
            try:
                done.add(json.loads(l)['id'])
            except Exception:
                pass
    todo = [i for i in ids if i not in done]
    print('%d records in the sitemap, %d already read, %d to read' % (len(ids), len(done), len(todo)), file=sys.stderr)
    q, lock, n, stop = queue.Queue(), threading.Lock(), [0], threading.Event()
    for i in todo:
        q.put(i)

    def worker():
        while not stop.is_set():
            try:
                i = q.get_nowait()
            except queue.Empty:
                return
            try:
                rec = fields(get('%s/concern/etds/%s?locale=en' % (ETD, i)))
            except urllib.error.HTTPError as e:
                if e.code == 403:                 # rate-limited: stop and leave the rest for a rerun
                    stop.set()
                    print('the site answered 403, stopping; rerun later to continue', file=sys.stderr)
                    return
                rec = {'error': e.code}
            except Exception:
                rec = {'error': 'timeout'}
            rec['id'] = i
            with lock:
                with open(out, 'a') as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
                n[0] += 1
                if n[0] % 500 == 0:
                    print(n[0], 'read', file=sys.stderr)
            time.sleep(a.pause)
    ts = [threading.Thread(target=worker) for _ in range(a.workers)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()


# fields that are not lab fields even when the name also says "mathematics" etc.
NOT_LAB = re.compile(r'econom|politic|history|philosoph|religio|english|literat|music|theater|film|classic|french|spanish|'
                     r'german|italian|russian|chinese|japanese|east asian|women|african american|american studies|jewish|'
                     r'middle eastern|art\b|dance', re.I)
# matches read against the thesis titles and found to be a different person with the same name
NOT_THE_SAME = {('Elizabeth Kim', 'Psychology')}

AFFIL = re.compile(r'\b(universit\w*|college|institute|school|center|centre|hospital|clinic|cdc|inc|llc|lab\w*|'
                   r'foundation|department|agency|centers|program|office|museum|library|ministry)\b', re.I)
TITLE = re.compile(r'^(dr|prof|professor|mr|mrs|ms|rev|rabbi)\.?\s+', re.I)


SUFFIX = re.compile(r'\s+(jr|sr|ii|iii|iv)\.?$', re.I)


def advisor(raw):
    """(name, at Emory?) from 'Dr. Jane Doe, Emory University', 'Doe, Jane' or 'Doe III, Jane'."""
    s = re.sub(r'\s+', ' ', re.sub(r"'[^']*'|\"[^\"]*\"", ' ', raw)).strip()     # drop quoted nicknames
    parts = [TITLE.sub('', p.strip()).strip() for p in s.split(',')]
    parts = [p for p in parts if p]
    if not parts:
        return '', False
    name, rest = SUFFIX.sub('', parts[0]), parts[1:]
    if rest and not AFFIL.search(rest[0]) and len(rest[0].split()) <= 3 and len(name.split()) == 1:
        name, rest = rest[0] + ' ' + name, rest[1:]          # "Doe, Jane"
    rest = [r for r in rest if not re.fullmatch(r'(ph\.?d|m\.?d|jr|sr|ii|iii|mph|ms|ma)\.?', r, re.I)]
    name = TITLE.sub('', name).strip()
    affil = ' '.join(rest)
    return name, (not affil) or bool(re.search(r'\bemory\b', affil, re.I))


# thesis fields where a lab scientist in the atlas plausibly advises; outside them, a name match counts only
# when the investigator also holds an Emory College appointment (otherwise it is likely a namesake, e.g. a
# political scientist and a psychiatrist with the same name)
LAB_FIELDS = re.compile(r'biolog|chemi|neuroscien|psycholog|physics|astronomy|environmental|human health|computer|'
                        r'mathemat|quantitative|data and decision|statistic|nursing|biomedical|health|engineering', re.I)


def college_appointment(atlas_page):
    """For each investigator: do they hold an Emory College (ECAS) appointment?"""
    d = json.loads(re.search(r'<script id="atlasdata" type="application/json">(.*?)</script>', atlas_page, re.S).group(1))
    ecas = {i for i, x in enumerate(d['insts']) if x['k'] == 'ECAS'}
    return [any(d['depts'][j]['i'] in ecas for j in p.get('d') or []) for p in d['pis']]


def merge(a):
    pis, vocab, H, page = read_atlas(a.atlas)
    names = Names(pis, vocab)
    in_college = college_appointment(page)
    recs = [json.loads(l) for l in open(os.path.join(a.cache, 'records.jsonl'))]
    # undergraduate honors theses: those filed through Emory College (a few graduate programs, e.g. public
    # health, also file an "honors thesis"; those are left out)
    honors = [r for r in recs if 'error' not in r and any('honors' in s.lower() for s in r.get('submission') or [])
              and (r.get('school') or [''])[0].strip() == 'Emory College']
    log, by_pi = collections.defaultdict(collections.Counter), collections.defaultdict(list)
    for r in honors:
        m = re.match(r'(Spring|Summer|Fall|Winter)\s+(\d{4})', r.get('term') or '')
        if m:
            term, y = m.group(1).lower(), int(m.group(2))
        elif r.get('year'):
            term, y = '', int(r['year'])     # older records give the year only
        else:
            log['no date'][r['id']] += 1
            continue
        dept = (r.get('dept') or [''])[0]
        seen = set()
        for raw in r.get('chair') or []:
            name, emory = advisor(raw)
            if not name or len(tokens(name)) < 2:
                log['not a name'][raw] += 1
                continue
            if not emory:
                log['outside Emory'][name] += 1
                continue
            pid, how = names.match(name)
            if pid is None:
                log['ambiguous' if how == 'ambiguous' else 'not in the atlas'][name] += 1
                continue
            if pid in seen:
                continue
            if how == 'spelling' and tokens(name)[-1:] != tokens(pis[pid]['n'])[-1:]:
                log['left out: surname spelled differently'][name + ' / ' + pis[pid]['n']] += 1
                continue
            if (name, dept) in NOT_THE_SAME:
                log['left out: checked by hand, a different person'][name + ' (' + dept + ')'] += 1
                continue
            if (NOT_LAB.search(dept) or not LAB_FIELDS.search(dept)) and not in_college[pid]:
                log['left out: same name, other field'][name + ' (' + (dept or 'no department') + ')'] += 1
                continue
            seen.add(pid)
            log['matched (' + how + ')'][name] += 1
            by_pi[pid].append({'y': y, 'term': term, 'program': 'Honors', 'title': r.get('title') or '',
                               'source': 'Honors thesis' + (', ' + dept if dept else ''), 'ns': 1,
                               'url': '%s/concern/etds/%s' % (ETD, r['id'])})

    # into the mentors list and the per-investigator history
    ref = H.get('ref_year') or max(x['y'] for v in by_pi.values() for x in v)
    mentors = [m for m in H.get('mentors', [])]
    for m in mentors:     # a rerun replaces the honors records it added before
        m['records'] = [x for x in m['records'] if x.get('program') != 'Honors']
    mentors = [m for m in mentors if m['records']]
    at = {m['pi_id']: m for m in mentors if m.get('pi_id') is not None}
    added = 0
    for pid, rs in by_pi.items():
        m = at.get(pid)
        if not m:
            m = {'name': pis[pid]['n'], 'pi_id': pid, 'programs': [], 'years': [], 'n_students': 0, 'records': []}
            mentors.append(m)
            at[pid] = m
            added += 1
        m['records'] = sorted(m['records'] + rs, key=lambda x: (-x['y'], x.get('title') or ''))
    for m in mentors:
        hon = sum(1 for x in m['records'] if x.get('program') == 'Honors')
        m['programs'] = sorted({x['program'] for x in m['records']}, key=lambda g: (g == 'Honors', g))
        m['years'] = sorted({x['y'] for x in m['records']})
    # students: the symposium count is kept as it was (distinct students), plus one per honors thesis
    old_n = {m['pi_id'] if m.get('pi_id') is not None else m['name']: m['n_students'] for m in H.get('mentors', [])}
    old_hon = {m['pi_id'] if m.get('pi_id') is not None else m['name']:
               sum(1 for x in m['records'] if x.get('program') == 'Honors') for m in H.get('mentors', [])}
    for m in mentors:
        k = m['pi_id'] if m.get('pi_id') is not None else m['name']
        base = old_n.get(k, 0) - old_hon.get(k, 0)
        m['n_students'] = base + sum(1 for x in m['records'] if x.get('program') == 'Honors')
    mentors.sort(key=lambda m: (-m['n_students'], m['name']))
    hist = {}
    for m in mentors:
        if m.get('pi_id') is None:
            continue
        ys = m['years']
        hist[str(m['pi_id'])] = dict(y=ys, t=sorted({x['term'] for x in m['records']}), n=len(m['records']),
                                     tier='RECENT' if ys[-1] >= ref - 3 else 'PAST',
                                     sure=any(x['program'] == 'SURE' for x in m['records']),
                                     honors=any(x['program'] == 'Honors' for x in m['records']),
                                     records=m['records'])
    caveat = re.sub(r'\s*Honors theses:.*$', '', H.get('source_caveat', ''))
    H.update(ref_year=ref, pis=hist, mentors=mentors,
             source_caveat=caveat + ' Honors theses: advisors of Emory College honors theses in Emory\'s theses and '
                                    'dissertations repository, matched to atlas investigators by name.')
    n_rec = sum(len(v) for v in by_pi.values())
    print('%d honors theses; %d advisor records matched to %d investigators (%d of them new to the mentors list)'
          % (len(honors), n_rec, len(by_pi), added), file=sys.stderr)
    if a.report:
        with open(a.report, 'w') as f:
            f.write('# Honors-thesis advisors\n\n%d honors theses read from %s, %d advisor records matched to %d atlas '
                    'investigators, %d of whom had no symposium record.\n\n' % (len(honors), ETD, n_rec, len(by_pi), added))
            for k in sorted(log):
                f.write('## %s (%d names, %d theses)\n\n' % (k, len(log[k]), sum(log[k].values())))
                for nm, c in log[k].most_common(60 if k.startswith('matched') else 40):
                    f.write('- %s (%d)\n' % (nm, c))
                f.write('\n')
    out = json.dumps(H, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(out)
    if a.write_atlas:
        new, n = re.subn(r'(<script id="surehist" type="application/json">)(.*?)(</script>)',
                         lambda mm: mm.group(1) + out + mm.group(3), page, count=1, flags=re.S)
        assert n == 1, 'no surehist block in the atlas'
        open(a.atlas, 'w', encoding='utf-8').write(new)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('crawl')
    c.add_argument('--cache', default='build/etd')
    c.add_argument('--workers', type=int, default=3)
    c.add_argument('--pause', type=float, default=0.6, help='seconds each worker waits between requests')
    m = sub.add_parser('merge')
    m.add_argument('--atlas', required=True)
    m.add_argument('--cache', default='build/etd')
    m.add_argument('--out', default=None, help='write the surehist block here as well')
    m.add_argument('--report', default=None)
    m.add_argument('--write-atlas', action='store_true')
    a = ap.parse_args()
    {'crawl': crawl, 'merge': merge}[a.cmd](a)


if __name__ == '__main__':
    main()
