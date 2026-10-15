"""PubMed's own year for every PubMed ID already on the atlas (esummary: print date and e-pub date, plus the
start of the title, which shows dead or mismatched IDs). v117's year correction came from this file, and merge.py
reads it (PUBMED_YEARS) to clear IDs that have no PubMed record. Resumable.

  python3 years.py <atlas.html>        # writes pubmed_years.json
"""
import re, json, time, urllib.request, urllib.parse, os, sys
t = open(sys.argv[1], encoding='utf-8').read()
d = json.loads(re.search(r'<script id="atlasdata" type="application/json">(.*?)</script>', t, re.S).group(1))
ids = sorted(set(e[3] for p in d['pis'] for e in p.get('p', []) if isinstance(e[3], int)))
OUT = 'pubmed_years.json'
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
todo = [i for i in ids if str(i) not in have]
print(len(ids), 'PMIDs,', len(todo), 'to fetch', flush=True)
for k in range(0, len(todo), 200):
    chunk = todo[k:k+200]
    body = urllib.parse.urlencode({'db': 'pubmed', 'retmode': 'json', 'id': ','.join(map(str, chunk))}).encode()
    for attempt in range(5):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi', data=body, headers={'User-Agent': 'LabAtlas year check'}), timeout=90))['result']
            break
        except Exception as e:
            time.sleep(2 + 3*attempt)
    else:
        print('failed chunk', k, flush=True); continue
    for i in chunk:
        rec = r.get(str(i)) or {}
        pd, ed = rec.get('pubdate', ''), rec.get('epubdate', '')
        have[str(i)] = {'pub': int(pd[:4]) if pd[:4].isdigit() else None, 'epub': int(ed[:4]) if ed[:4].isdigit() else None,
                        'title': (rec.get('title') or '')[:80]}
    if (k // 200) % 20 == 0:
        json.dump(have, open(OUT, 'w')); print(k + len(chunk), 'done', flush=True)
    time.sleep(0.4)
json.dump(have, open(OUT, 'w')); print('finished', len(have), flush=True)
