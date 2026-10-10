#!/usr/bin/env python3
"""Keep the shared Google Drive folder and this repository in step.

  push    upload a Lab Atlas version to the folder, and add it to the folder's
          version log ("Lab Atlas versions.md"), so every version can be seen there
  pull    find Lab Atlas HTML files in the folder (any subfolder) that this
          pipeline did not put there, e.g. a collaborator's build, and download them
  merge   three-way merge one of those files into the repository's current version
  sync    pull, merge each new file in turn, and push the result: what the
          scheduled GitHub workflow runs (.github/workflows/drive-sync.yml)

How a merge works
  An atlas file is a page (styles and markup), a data block (the records), the
  mentoring block, and the page's scripts. Every collaborator's file started from
  some earlier version, so the merge first finds that version: whichever file in
  this repository's history (or already in the folder) shares the most with it.
  With that as the common base:
    - the page and its scripts are merged line by line (git merge-file);
    - the records are merged person by person and field by field: a field only
      they changed takes their value, one only we changed keeps ours, and people
      only they added are appended (record numbers are never reshuffled);
    - other data tables are taken from whichever side changed them;
    - where both sides changed the same thing differently, ours is kept and the
      clash is listed in the report.
  The merged file must parse and its scripts must pass `node --check`, or nothing
  is written.

Credentials (never stored in the repository)
  The folder belongs to an ordinary Google account, so the pipeline signs in as a
  person, not a service account (service accounts cannot own files there):
    GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET   an OAuth client of type "Desktop app"
    GDRIVE_REFRESH_TOKEN                     from `python3 scripts/drive_sync.py auth`
    GDRIVE_FOLDER_ID                         the shared folder's id
  For a Shared Drive a service account works instead: GDRIVE_SA_TOKEN (an access
  token minted by the workflow) takes the place of the three OAuth values.

Usage
  python3 scripts/drive_sync.py auth                       # once, on your machine
  python3 scripts/drive_sync.py push Emory_Lab_Atlas_v103.html
  python3 scripts/drive_sync.py pull --to build/incoming
  python3 scripts/drive_sync.py merge build/incoming/X.html --ours Emory_Lab_Atlas_v103.html \\
      --out Emory_Lab_Atlas_v103.html --report build/merge_report.md
  python3 scripts/drive_sync.py sync                       # all of the above, as the workflow does
  Any command takes --local DIR to use a plain folder instead of Drive (tests).
"""
import argparse, collections, datetime, hashlib, http.server, json, os, re, shutil, subprocess, sys, tempfile, threading, urllib.parse, urllib.request, webbrowser

ATLAS_RE = re.compile(r'Emory_Lab_Atlas_v(\d+)[^/]*\.html$', re.I)
STATE_NAME = '.labatlas-sync.json'       # in the folder: which files the pipeline wrote or has merged
LOG_NAME = 'Lab Atlas versions.md'       # in the folder: one line per version, newest first

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

# ---------------------------------------------------------------- storage
class Drive:
    API = 'https://www.googleapis.com/drive/v3'
    UP = 'https://www.googleapis.com/upload/drive/v3'
    def __init__(self, folder):
        self.folder = folder; self._tok = None
    def token(self):
        if self._tok: return self._tok
        if os.environ.get('GDRIVE_SA_TOKEN'):
            self._tok = os.environ['GDRIVE_SA_TOKEN']; return self._tok
        need = ['GDRIVE_CLIENT_ID', 'GDRIVE_CLIENT_SECRET', 'GDRIVE_REFRESH_TOKEN']
        miss = [k for k in need if not os.environ.get(k)]
        if miss: sys.exit('missing credentials: ' + ', '.join(miss) + ' (see the top of this file)')
        body = urllib.parse.urlencode({'grant_type': 'refresh_token', 'refresh_token': os.environ['GDRIVE_REFRESH_TOKEN'],
                                       'client_id': os.environ['GDRIVE_CLIENT_ID'], 'client_secret': os.environ['GDRIVE_CLIENT_SECRET']}).encode()
        r = json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', body, timeout=60))
        self._tok = r['access_token']; return self._tok
    def req(self, method, url, data=None, headers=None, raw=False):
        h = {'Authorization': 'Bearer ' + self.token()}; h.update(headers or {})
        rq = urllib.request.Request(url, data=data, method=method, headers=h)
        r = urllib.request.urlopen(rq, timeout=600)
        return r if raw else json.load(r)
    def children(self, folder):
        out, tok = [], None
        while True:
            q = urllib.parse.urlencode({'q': "'%s' in parents and trashed=false" % folder, 'pageSize': 200,
                'fields': 'nextPageToken,files(id,name,mimeType,md5Checksum,size,modifiedTime,owners(emailAddress),lastModifyingUser(emailAddress))',
                'supportsAllDrives': 'true', 'includeItemsFromAllDrives': 'true', **({'pageToken': tok} if tok else {})})
            r = self.req('GET', self.API + '/files?' + q)
            out += r.get('files', []); tok = r.get('nextPageToken')
            if not tok: return out
    def walk(self, folder=None, path=''):
        for f in self.children(folder or self.folder):
            p = path + f['name']
            if f['mimeType'] == 'application/vnd.google-apps.folder': yield from self.walk(f['id'], p + '/')
            else: f['path'] = p; yield f
    def download(self, fid, dest):
        r = self.req('GET', self.API + '/files/%s?alt=media&supportsAllDrives=true' % fid, raw=True)
        with open(dest, 'wb') as out: shutil.copyfileobj(r, out, 1 << 20)
    def upload(self, src, name, mime='text/html', fid=None):
        meta = json.dumps({'name': name} if fid else {'name': name, 'parents': [self.folder]}).encode()
        url = self.UP + ('/files/%s?uploadType=resumable&supportsAllDrives=true' % fid if fid else '/files?uploadType=resumable&supportsAllDrives=true')
        r = self.req('PATCH' if fid else 'POST', url, meta, {'Content-Type': 'application/json; charset=UTF-8', 'X-Upload-Content-Type': mime}, raw=True)
        loc, size, CH = r.headers['Location'], os.path.getsize(src), 8 << 20
        with open(src, 'rb') as f:
            off = 0
            while True:
                chunk = f.read(CH); end = off + len(chunk) - 1
                rq = urllib.request.Request(loc, data=chunk, method='PUT', headers={'Content-Range': 'bytes %d-%d/%d' % (off, end, size) if chunk else 'bytes */%d' % size})
                try:
                    resp = urllib.request.urlopen(rq, timeout=600); return json.load(resp)
                except urllib.error.HTTPError as e:
                    if e.code != 308: raise
                off = end + 1
    def find(self, name):
        return next((f for f in self.children(self.folder) if f['name'] == name), None)

class Local:
    """A plain folder standing in for Drive, for tests and dry runs."""
    def __init__(self, root): self.root = root; os.makedirs(root, exist_ok=True)
    def walk(self):
        for dp, _, fs in os.walk(self.root):
            for n in fs:
                p = os.path.join(dp, n); rel = os.path.relpath(p, self.root)
                yield {'id': rel, 'name': n, 'path': rel, 'md5Checksum': md5(p), 'size': str(os.path.getsize(p)),
                       'modifiedTime': datetime.datetime.utcfromtimestamp(os.path.getmtime(p)).isoformat() + 'Z',
                       'lastModifyingUser': {'emailAddress': 'local'}}
    def download(self, fid, dest): shutil.copy(os.path.join(self.root, fid), dest)
    def upload(self, src, name, mime='text/html', fid=None):
        shutil.copy(src, os.path.join(self.root, fid or name)); return {'id': fid or name, 'name': name}
    def find(self, name):
        return {'id': name, 'name': name} if os.path.exists(os.path.join(self.root, name)) else None

def store(a):
    if a.local: return Local(a.local)
    folder = a.folder or os.environ.get('GDRIVE_FOLDER_ID')
    if not folder: sys.exit('no folder: pass --folder or set GDRIVE_FOLDER_ID')
    return Drive(folder)

def read_state(s, tmp):
    f = s.find(STATE_NAME)
    if not f: return {'pushed': {}, 'merged': {}}, None
    p = os.path.join(tmp, STATE_NAME); s.download(f['id'], p)
    return json.load(open(p)), f['id']

def write_state(s, tmp, state, fid):
    p = os.path.join(tmp, STATE_NAME); json.dump(state, open(p, 'w'), indent=1, sort_keys=True)
    s.upload(p, STATE_NAME, 'application/json', fid)

# ---------------------------------------------------------------- the file's parts
DATA_RE = re.compile(r'(<script id="atlasdata" type="application/json">)(.*?)(</script>)', re.S)
SURE_RE = re.compile(r'(<script id="surehist" type="application/json">)(.*?)(</script>)', re.S)

def split(html):
    m = DATA_RE.search(html)
    if not m: raise ValueError('not an atlas file: no atlasdata block')
    head, data, tail = html[:m.start()], m.group(2), html[m.end():]
    ms = SURE_RE.search(tail)
    sure = ms.group(2) if ms else None
    if ms: tail = tail[:ms.start()] + '<!--SUREHIST-->' + tail[ms.end():]
    return {'head': head, 'data': data, 'sure': sure, 'tail': tail}

def join(p):
    tail = p['tail'].replace('<!--SUREHIST-->', '<script id="surehist" type="application/json">' + (p['sure'] or '') + '</script>') if p['sure'] is not None else p['tail']
    return p['head'] + '<script id="atlasdata" type="application/json">' + p['data'] + '</script>' + tail

def text_lines(s):
    # long minified lines merge badly; break them at statement and tag boundaries so a change is a few lines, not one
    # (each inserted break carries U+E000, so exactly those, and no original newline, are removed on the way back)
    return re.sub(r'(;|\}|>)(?=\S)', '\\1\n\ue000', s).split('\n')

def similarity(a, b):
    la, lb = set(text_lines(a['head'] + a['tail'])), set(text_lines(b['head'] + b['tail']))
    t = len(la & lb) / max(1, len(la | lb))
    try:
        pa, pb = json.loads(a['data'])['pis'], json.loads(b['data'])['pis']
        same = sum(1 for x, y in zip(pa, pb) if x == y) / max(1, max(len(pa), len(pb)))
    except Exception: same = 0
    return t*.5 + same*.5

def history(repo, pattern='Emory_Lab_Atlas_v*.html', limit=40):
    """(label, html) for each atlas version in git history, newest first."""
    try:
        log = subprocess.run(['git', '-C', repo, 'log', '--all', '--format=%H', '-n', str(limit), '--', pattern], capture_output=True, text=True, check=True).stdout.split()
    except Exception: return
    seen = set()
    for c in log:
        names = subprocess.run(['git', '-C', repo, 'ls-tree', '--name-only', c], capture_output=True, text=True).stdout.split()
        for n in names:
            if ATLAS_RE.search(n) and (c, n) not in seen:
                seen.add((c, n))
                blob = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (c, n)], capture_output=True).stdout
                if blob: yield '%s@%s' % (n, c[:7]), blob.decode('utf-8', 'replace')

# ---------------------------------------------------------------- merging
def merge_text(ours, base, theirs, label):
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for n, s in (('ours', ours), ('base', base), ('theirs', theirs)):
            p = os.path.join(d, n); open(p, 'w', encoding='utf-8').write('\n'.join(text_lines(s))); paths.append(p)
        dry = subprocess.run(['git', 'merge-file', '-p', '--diff3', *paths], capture_output=True)
        conflicts = dry.returncode if dry.returncode > 0 else 0
        res = subprocess.run(['git', 'merge-file', '-p', '--ours', *paths], capture_output=True)
        out = res.stdout.decode('utf-8')
    # rejoin the breaks text_lines made
    out = out.replace('\n\ue000', '')
    return out, conflicts

def rec_key(p):
    return ('e', str(p.get('e')).lower()) if p.get('e') else ('n', str(p.get('n')).lower())

def merge_data(ours, base, theirs, rep):
    O, B, T = json.loads(ours), json.loads(base), json.loads(theirs)
    out = dict(O)
    for k in sorted(set(O) | set(T)):
        o, b, t = O.get(k), B.get(k), T.get(k)
        if k == 'pis': continue
        if t == b or t == o: continue
        if o == b: out[k] = t; rep['taken from theirs'].append('data table `%s`' % k)
        else: rep['clashes (ours kept)'].append('data table `%s` changed on both sides' % k)
    # the people, field by field
    po, pb, pt = O.get('pis', []), B.get('pis', []), T.get('pis', [])
    bi = {rec_key(p): p for p in pb}; ti = {rec_key(p): p for p in pt}
    merged = []
    for p in po:
        k = rec_key(p); b = bi.get(k); t = ti.get(k)
        if t is None or b is None or t == b: merged.append(p); continue
        q = dict(p)
        for f in sorted(set(p) | set(t) | set(b)):
            vo, vb, vt = p.get(f, None), b.get(f, None), t.get(f, None)
            if vt == vb or vt == vo: continue
            if vo == vb:
                if vt is None: q.pop(f, None)
                else: q[f] = vt
                rep['fields taken from theirs'].append('%s: %s' % (p.get('n'), f))
            else: rep['clashes (ours kept)'].append('%s: %s changed on both sides' % (p.get('n'), f))
        merged.append(q)
    have = {rec_key(p) for p in po}
    for p in pt:
        if rec_key(p) not in have and rec_key(p) not in bi:
            merged.append(p); rep['people added by them'].append(p.get('n'))
    gone = [p.get('n') for p in pb if rec_key(p) not in ti and rec_key(p) in have]
    if gone: rep['people they removed (kept)'].extend(gone)
    out['pis'] = merged
    return json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

def merge_sure(o, b, t, rep):
    if t is None or t == b or t == o: return o
    if o == b or o is None: rep['taken from theirs'].append('mentoring block'); return t
    rep['clashes (ours kept)'].append('mentoring block changed on both sides'); return o

def check(html):
    p = split(html); json.loads(p['data'])
    if p['sure']: json.loads(p['sure'])
    with tempfile.TemporaryDirectory() as d:
        for i, m in enumerate(re.finditer(r'<script>(.*?)</script>', html, re.S)):
            f = os.path.join(d, '%d.js' % i); open(f, 'w', encoding='utf-8').write(m.group(1))
            r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
            if r.returncode: raise ValueError('script %d does not parse: %s' % (i, r.stderr.strip()[:300]))

def do_merge(theirs_path, ours_path, out_path, report_path, repo='.', extra_bases=()):
    T = split(open(theirs_path, encoding='utf-8').read()); O = split(open(ours_path, encoding='utf-8').read())
    best = None
    for label, html in list(history(repo)) + list(extra_bases):
        try: B = split(html)
        except ValueError: continue
        s = similarity(B, T)
        if not best or s > best[0]: best = (s, label, B)
    if not best: sys.exit('no earlier version to merge against')
    s, label, B = best
    rep = collections.defaultdict(list)
    head, c1 = merge_text(O['head'], B['head'], T['head'], 'head')
    tail, c2 = merge_text(O['tail'], B['tail'], T['tail'], 'tail')
    if c1 or c2: rep['clashes (ours kept)'].append('%d clashing hunk(s) in the page and %d in its scripts' % (c1, c2))
    for part, a, b in (('page (styles and markup)', O['head'], head), ('scripts', O['tail'], tail)):
        if a != b: rep['taken from theirs'].append(part + ': their line changes merged in')
    merged = {'head': head, 'tail': tail, 'data': merge_data(O['data'], B['data'], T['data'], rep), 'sure': merge_sure(O['sure'], B['sure'], T['sure'], rep)}
    html = join(merged)
    check(html)
    open(out_path, 'w', encoding='utf-8').write(html)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# Merge of %s\n\nInto `%s`. Common base: `%s` (similarity %.2f).\n\n' % (os.path.basename(theirs_path), os.path.basename(ours_path), label, s))
        for k in ('taken from theirs', 'fields taken from theirs', 'people added by them', 'people they removed (kept)', 'clashes (ours kept)'):
            v = rep.get(k, [])
            f.write('## %s (%d)\n\n' % (k[0].upper() + k[1:], len(v)))
            f.writelines('- %s\n' % x for x in v[:400]); f.write(('- ... and %d more\n' % (len(v) - 400)) if len(v) > 400 else '')
            f.write('\n')
    return rep

# ---------------------------------------------------------------- commands
def cmd_push(a):
    s = store(a); tmp = tempfile.mkdtemp()
    state, sid = read_state(s, tmp)
    name = a.name or os.path.basename(a.file)
    if md5(a.file) in state['pushed']:
        print('already in the folder:', state['pushed'][md5(a.file)]['name']); return
    f = s.upload(a.file, name)
    state['pushed'][md5(a.file)] = {'name': name, 'id': f.get('id'), 'at': datetime.datetime.utcnow().isoformat() + 'Z',
                                    'commit': os.environ.get('GITHUB_SHA', '')[:7], 'note': a.note or ''}
    write_state(s, tmp, state, sid)
    # the version log people read
    lines = ['# Lab Atlas versions\n', 'Newest first. Every version the pipeline publishes, and every file merged in from this folder.\n',
             '| Version | Published (UTC) | From | Note |', '|---|---|---|---|']
    rows = sorted([(v['at'], v['name'], 'repository ' + (v.get('commit') or ''), v.get('note', '')) for v in state['pushed'].values()] +
                  [(v['at'], v['name'], 'the folder' + (' (' + v['by'] + ')' if v.get('by') else ''), 'merged into ' + v.get('into', '')) for v in state['merged'].values()], reverse=True)
    lines += ['| %s | %s | %s | %s |' % (n, at[:16].replace('T', ' '), fr, note) for at, n, fr, note in rows]
    lp = os.path.join(tmp, 'versions.md'); open(lp, 'w').write('\n'.join(lines) + '\n')
    lf = s.find(LOG_NAME); s.upload(lp, LOG_NAME, 'text/markdown', lf['id'] if lf else None)
    print('pushed', name)

def cmd_pull(a):
    s = store(a); tmp = tempfile.mkdtemp(); os.makedirs(a.to, exist_ok=True)
    state, _ = read_state(s, tmp)
    known = set(state['pushed']) | set(state['merged'])
    got = []
    for f in s.walk():
        if not ATLAS_RE.search(f['name']): continue
        if f.get('md5Checksum') in known: continue
        dest = os.path.join(a.to, f['name']); s.download(f['id'], dest)
        if md5(dest) in known: os.remove(dest); continue
        got.append({'path': dest, 'md5': md5(dest), 'name': f['name'], 'by': (f.get('lastModifyingUser') or {}).get('emailAddress', '')})
        print('new in the folder:', f.get('path', f['name']))
    json.dump(got, open(os.path.join(a.to, 'incoming.json'), 'w'), indent=1)
    return got

def latest_version(repo):
    vs = [(int(m.group(1)), n) for n in os.listdir(repo) for m in [ATLAS_RE.search(n)] if m]
    return max(vs) if vs else (None, None)

def cmd_sync(a):
    repo = a.repo
    a.to = a.to or os.path.join(repo, 'build', 'incoming')
    got = cmd_pull(a)
    s = store(a); tmp = tempfile.mkdtemp()
    for g in got:
        v, cur = latest_version(repo)
        nxt = 'Emory_Lab_Atlas_v%d.html' % (v + 1)
        rp = os.path.join(repo, 'docs', 'merges', 'merge_%s.md' % re.sub(r'\W+', '_', g['name'])); os.makedirs(os.path.dirname(rp), exist_ok=True)
        try:
            do_merge(g['path'], os.path.join(repo, cur), os.path.join(repo, nxt), rp, repo)
        except Exception as e:
            print('could not merge', g['name'], ':', e); continue
        subprocess.run(['git', '-C', repo, 'rm', '-q', cur], check=False)
        state, sid = read_state(s, tmp)
        state['merged'][g['md5']] = {'name': g['name'], 'by': g['by'], 'into': nxt, 'at': datetime.datetime.utcnow().isoformat() + 'Z'}
        write_state(s, tmp, state, sid)
        print('merged', g['name'], 'into', nxt, '- report', rp)
        a.file, a.name, a.note = os.path.join(repo, nxt), nxt, 'merged ' + g['name']
        cmd_push(a)

def cmd_merge(a):
    rep = do_merge(a.theirs, a.ours, a.out, a.report, a.repo)
    print('merged; report:', a.report, {k: len(v) for k, v in rep.items()})

def cmd_auth(a):
    """One-time sign-in on your own machine: prints the refresh token to store as GDRIVE_REFRESH_TOKEN."""
    cid, sec = os.environ.get('GDRIVE_CLIENT_ID'), os.environ.get('GDRIVE_CLIENT_SECRET')
    if not cid or not sec: sys.exit('set GDRIVE_CLIENT_ID and GDRIVE_CLIENT_SECRET first (an OAuth client of type "Desktop app")')
    got = {}
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            got.update(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query))
            self.send_response(200); self.end_headers(); self.wfile.write(b'Signed in. You can close this tab.')
        def log_message(self, *x): pass
    srv = http.server.HTTPServer(('127.0.0.1', 0), H); port = srv.server_address[1]
    redirect = 'http://127.0.0.1:%d/' % port
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode({'client_id': cid, 'redirect_uri': redirect, 'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/drive', 'access_type': 'offline', 'prompt': 'consent'})
    print('Open this and sign in with an account that can edit the folder:\n' + url); webbrowser.open(url)
    threading.Thread(target=srv.handle_request).start()
    while 'code' not in got and 'error' not in got: pass
    if 'error' in got: sys.exit('sign-in refused: %s' % got['error'])
    r = json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', urllib.parse.urlencode({'code': got['code'][0], 'client_id': cid,
        'client_secret': sec, 'redirect_uri': redirect, 'grant_type': 'authorization_code'}).encode()))
    print('\nGDRIVE_REFRESH_TOKEN=' + r['refresh_token'] + '\n\nStore it as a repository secret; do not commit it.')

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--local', help='use this folder instead of Drive')
    ap.add_argument('--folder', help='the Drive folder id (default: $GDRIVE_FOLDER_ID)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('push'); p.add_argument('file'); p.add_argument('--name'); p.add_argument('--note')
    p = sub.add_parser('pull'); p.add_argument('--to', default='build/incoming')
    p = sub.add_parser('merge'); p.add_argument('theirs'); p.add_argument('--ours', required=True); p.add_argument('--out', required=True)
    p.add_argument('--report', default='build/merge_report.md'); p.add_argument('--repo', default='.')
    p = sub.add_parser('sync'); p.add_argument('--repo', default='.'); p.add_argument('--to')
    sub.add_parser('auth')
    a = ap.parse_args()
    {'push': cmd_push, 'pull': cmd_pull, 'merge': cmd_merge, 'sync': cmd_sync, 'auth': cmd_auth}[a.cmd](a)

if __name__ == '__main__':
    main()
