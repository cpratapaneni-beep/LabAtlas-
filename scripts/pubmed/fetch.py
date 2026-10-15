"""Phase B: the full PubMed record of every candidate paper not already on file: title, year, journal, DOI and each
author's name and own affiliations (needed to check that the investigator, not a namesake, wrote it). Resumable."""
import json, os, sys, time, urllib.request, urllib.parse, threading, xml.etree.ElementTree as ET
cands = set()
for fn in sys.argv[1:]:   # search.jsonl files
    for l in open(fn):
        r = json.loads(l); cands.update(str(i) for i in r.get('ids', []))
OUT = 'records.jsonl'
have = set()
if os.path.exists(OUT):
    for l in open(OUT):
        try: have.add(json.loads(l)['pmid'])
        except Exception: pass
todo = sorted(cands - have)          # existing papers too: their author lists are needed for the same check
print(len(cands), 'candidates,', len(todo), 'to fetch', flush=True)
def txt(e): return ''.join(e.itertext()).strip() if e is not None else ''
def parse(xml):
    out = []
    root = ET.fromstring(xml)
    for art in root.iter('PubmedArticle'):
        mc = art.find('MedlineCitation'); a = mc.find('Article')
        pmid = mc.findtext('PMID')
        y = a.findtext('Journal/JournalIssue/PubDate/Year') or (a.findtext('Journal/JournalIssue/PubDate/MedlineDate') or '')[:4]
        doi = ''
        for i in art.iter('ArticleId'):
            if i.get('IdType') == 'doi': doi = (i.text or '').strip()
        auths = []
        for au in a.iter('Author'):
            auths.append([au.findtext('LastName') or '', au.findtext('ForeName') or '', au.findtext('Initials') or '',
                          [txt(af) for af in au.iter('Affiliation')]])
        out.append({'pmid': pmid, 'title': txt(a.find('ArticleTitle')), 'year': int(y) if (y or '')[:4].isdigit() else None,
                    'journal': a.findtext('Journal/ISOAbbreviation') or a.findtext('Journal/Title') or '', 'doi': doi, 'authors': auths})
    return out
lock = threading.Lock(); last = [0.0]; f = open(OUT, 'a'); n = [0]
chunks = [todo[k:k+150] for k in range(0, len(todo), 150)]
def worker():
    while True:
        with lock:
            if not chunks: return
            ch = chunks.pop()
        for attempt in range(6):
            with lock:
                w = last[0] + 0.36 - time.time()
                if w > 0: time.sleep(w)
                last[0] = time.time()
            try:
                body = urllib.parse.urlencode({'db': 'pubmed', 'retmode': 'xml', 'id': ','.join(ch)}).encode()
                xml = urllib.request.urlopen(urllib.request.Request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi', data=body, headers={'User-Agent': 'LabAtlas publications'}), timeout=120).read()
                recs = parse(xml); break
            except Exception as e:
                recs = None; time.sleep(3 + 4*attempt)
        if recs is None: print('failed chunk', ch[0], flush=True); continue
        with lock:
            for r in recs: f.write(json.dumps(r, ensure_ascii=False) + '\n')
            f.flush(); n[0] += len(ch)
            if n[0] % 15000 < 150: print(n[0], 'fetched', flush=True)
ts = [threading.Thread(target=worker) for _ in range(3)]
[t.start() for t in ts]; [t.join() for t in ts]
print('done', flush=True)
