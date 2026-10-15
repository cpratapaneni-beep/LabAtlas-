"""After merge.py adds faculty: point their symposium mentor rows at the new profiles (same name), so the honors
merge that follows rebuilds their mentoring history under the profile. Usage: link_mentors.py <atlas.html>"""
import json, re, sys, unicodedata
path = sys.argv[1]
t = open(path, encoding='utf-8').read()
d = json.loads(re.search(r'<script id="atlasdata" type="application/json">(.*?)</script>', t, re.S).group(1))
m = re.search(r'(<script id="surehist" type="application/json">)(.*?)(</script>)', t, re.S)
H = json.loads(m.group(2))
norm = lambda s: re.sub(r'[^a-z]+', '', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower())
new = {}
for i, p in enumerate(d['pis']):
    if p.get('v118') == 'mentor':
        for v in p.get('v118names') or [p['n']]: new[norm(v)] = i
n = 0
for mm in H['mentors']:
    if mm.get('pi_id') is None and norm(mm['name']) in new:
        mm['pi_id'] = new[norm(mm['name'])]; n += 1
out = json.dumps(H, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
t = t[:m.start(2)] + out + t[m.end(2):]
open(path, 'w', encoding='utf-8').write(t)
print('symposium mentor rows linked to new profiles:', n)
