"""Step 1: one PubMed search per person (see names.query). Resumable; at most 3 requests a second (NCBI's limit
without an API key).

  python3 search.py pi_names.json search.jsonl
  python3 search.py outside_mentors.json mentor_search.jsonl
"""
import json, os, sys, time, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from names import query
names = json.load(open(sys.argv[1]))
names = [n if isinstance(n, str) else n['name'] for n in names]
OUT = sys.argv[2]
done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        try: done.add(json.loads(l)['i'])
        except Exception: pass
import threading, queue
lock = threading.Lock(); q = queue.Queue(); cnt = [0]
for i, name in enumerate(names):
    if i not in done: q.put((i, name))
out = open(OUT, 'a')
last = [0.0]
def worker():
    while True:
        try: i, name = q.get_nowait()
        except queue.Empty: return
        qq = query(name); rec = {'i': i, 'n': name, 'q': qq}
        if qq:
            for attempt in range(6):
                with lock:   # space requests at least 0.34 s apart across all workers (NCBI: 3 a second)
                    wait = last[0] + 0.34 - time.time()
                    if wait > 0: time.sleep(wait)
                    last[0] = time.time()
                try:
                    body = urllib.parse.urlencode({'db': 'pubmed', 'retmode': 'json', 'retmax': 10000, 'term': qq}).encode()
                    r = json.load(urllib.request.urlopen(urllib.request.Request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', data=body, headers={'User-Agent': 'LabAtlas publications'}), timeout=60))['esearchresult']
                    rec['count'] = int(r.get('count', 0)); rec['ids'] = [int(x) for x in r.get('idlist', [])]; rec.pop('err', None)
                    break
                except Exception as e:
                    rec['err'] = str(e)[:80]; time.sleep(2 + 3*attempt)
        with lock:
            out.write(json.dumps(rec) + '\n'); out.flush(); cnt[0] += 1
            if cnt[0] % 500 == 0: print(cnt[0], 'searched', flush=True)
ts = [threading.Thread(target=worker) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
print('done', flush=True)
