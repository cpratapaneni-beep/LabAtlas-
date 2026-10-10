#!/usr/bin/env python3
"""Build a deployable site from the single-file atlas.

The single HTML file is easy to pass around but slow to open on a phone: 37 MB
in one piece, and nothing is drawn until all of it has arrived. This splits it
for a web server:

  site/index.html          the page itself, without data or code (~0.5 MB):
                           the landing is readable as soon as it arrives
  site/data/atlas.json     the records          (fetched once, then cached)
  site/data/surehist.json  the mentoring record
  site/app/0.js ... n.js   the page's scripts, run in their original order
  site/departments/*.html  one plain page per department: who is there, and how
                           many work at the bench or at a computer. Readable by
                           search engines and AI assistants without JavaScript
  site/sitemap.xml, robots.txt, og-image.png

Searching or opening the atlas before the data has arrived is remembered and
done as soon as it lands.

Usage
  python3 scripts/build_site.py --atlas Emory_Lab_Atlas_v103.html --out site \\
      --site-url https://labatlas.example.edu/
  (--site-url makes the share image and canonical links absolute, which link
   previews need; leave it out for a local preview: python3 -m http.server -d site)
Serve the folder with gzip or brotli on (any static host does: GitHub Pages,
Netlify, Cloudflare Pages, S3+CloudFront); the data then travels at ~9 MB once.
"""
import argparse, html, json, os, re, shutil, sys, unicodedata

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:70] or 'unit'

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--atlas', required=True)
    ap.add_argument('--out', default='site')
    ap.add_argument('--site-url', default='', help='where the site will live, e.g. https://labatlas.example.edu/')
    ap.add_argument('--og-image', default='og-image.png', help='the share image to copy in (made by scripts/og_image.mjs)')
    a = ap.parse_args()
    base = a.site_url.rstrip('/') + '/' if a.site_url else ''
    page = open(a.atlas, encoding='utf-8').read()
    os.makedirs(os.path.join(a.out, 'data'), exist_ok=True)
    os.makedirs(os.path.join(a.out, 'app'), exist_ok=True)
    os.makedirs(os.path.join(a.out, 'departments'), exist_ok=True)

    # 1. pull the data blocks out
    blocks = {}
    for bid in ('atlasdata', 'surehist'):
        m = re.search(r'<script id="%s" type="application/json">(.*?)</script>' % bid, page, re.S)
        if not m: sys.exit('no %s block in %s' % (bid, a.atlas))
        blocks[bid] = m.group(1).replace('<\\/', '</')
        open(os.path.join(a.out, 'data', bid.replace('atlasdata', 'atlas') + '.json'), 'w', encoding='utf-8').write(blocks[bid])
        page = page[:m.start()] + page[m.end():]

    # 2. every script after <head> becomes a file, loaded in order once the data is in
    head_end = page.index('</head>')
    files = []
    def take(m):
        if m.start() < head_end: return m.group(0)          # the theme script stays inline, so there is no flash
        n = len(files)
        open(os.path.join(a.out, 'app', '%d.js' % n), 'w', encoding='utf-8').write(m.group(2))
        files.append('app/%d.js' % n)
        return ''
    page = re.sub(r'<script([^>]*)>(.*?)</script>', take, page, flags=re.S)
    loader = '''<div class="v94-loading" id="v94Loading" role="status">Loading the atlas&hellip;</div>
<style>.v94-loading{position:fixed;left:50%%;bottom:18px;transform:translateX(-50%%);z-index:200;padding:8px 14px;border-radius:999px;
background:#031b36;color:#fdffee;font:500 13px/1 system-ui,sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.3)}.v94-loading[hidden]{display:none}</style>
<script>
(function(){
  /* anything asked for before the atlas has loaded is remembered and done when it has */
  var pending = null;
  function hold(e){ var t = e.target.closest && e.target.closest('[data-open],[data-doc],form#lpAskForm,.lp-topic'); if(!t) return;
    if(window.__atlasReady) return; e.preventDefault(); e.stopPropagation(); pending = t; document.getElementById('v94Loading').textContent = 'Loading the atlas\\u2026 one moment'; }
  document.addEventListener('click', hold, true); document.addEventListener('submit', hold, true);
  function add(id, text){ var s = document.createElement('script'); s.type = 'application/json'; s.id = id; s.textContent = text; document.body.appendChild(s); }
  function run(src){ return new Promise(function(ok, no){ var s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.body.appendChild(s); }); }
  Promise.all([fetch('data/atlas.json').then(function(r){ return r.text(); }), fetch('data/surehist.json').then(function(r){ return r.text(); })])
    .then(function(d){ add('atlasdata', d[0]); add('surehist', d[1]);
      return %s.reduce(function(p, f){ return p.then(function(){ return run(f); }); }, Promise.resolve()); })
    .then(function(){ window.__atlasReady = true; document.getElementById('v94Loading').hidden = true;
      if(pending){ var t = pending; pending = null; if(t.tagName === 'FORM') t.requestSubmit(); else t.click(); } })
    .catch(function(){ document.getElementById('v94Loading').textContent = 'The atlas could not load. Check your connection and reload.'; });
})();
</script>
''' % json.dumps(files)
    page = page.replace('</body>', loader + '</body>', 1)
    if base:
        page = page.replace('content="og-image.png"', 'content="%sog-image.png"' % base)
        page = page.replace('<meta name="theme-color"', '<link rel="canonical" href="%s">\n<meta name="theme-color"' % base, 1)
    open(os.path.join(a.out, 'index.html'), 'w', encoding='utf-8').write(page)

    # 3. one page per department
    D = json.loads(blocks['atlasdata'])
    P, DEPTS, INSTS = D['pis'], D['depts'], D['insts']
    side = lambda l: 'bench' if l in (1, 4) else 'computational, clinical or population' if l in (2, 5) else 'hybrid' if l == 3 else 'unclassified'
    groups = {}
    for di, d in enumerate(DEPTS):
        key = (re.sub(r'\s+', ' ', d['n']).strip(), d['i'])
        groups.setdefault(key, []).append(di)
    pages = []
    for (name, ii), dis in sorted(groups.items()):
        ds = set(dis)
        people = sorted([p for p in P if ds & set(p.get('d') or [])], key=lambda p: p['n'])
        if len(people) < 3: continue
        cnt = {}
        for p in people: cnt[side(p.get('l') or 0)] = cnt.get(side(p.get('l') or 0), 0) + 1
        inst = INSTS[ii]['label']
        s = slug(name + ' ' + INSTS[ii]['k'])
        title = 'Emory labs in %s (%s): %d investigators' % (name, inst, len(people))
        summary = '%d investigators in %s, %s. %d work mainly at the bench, %d are hybrid, %d do computational, clinical or population research, and %d have too little on record to place.' % (
            len(people), name, inst, cnt.get('bench', 0), cnt.get('hybrid', 0), cnt.get('computational, clinical or population', 0), cnt.get('unclassified', 0))
        rows = ''.join('<li><b>%s</b>%s <span>%s</span></li>' % (
            html.escape(p['n']), (' &middot; ' + html.escape(p['g'])) if p.get('g') else '', side(p.get('l') or 0)) for p in people)
        doc = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><meta name="description" content="%s">%s
<style>body{margin:0;font:16px/1.55 system-ui,sans-serif;color:#031b36;background:#fdffee}main{max-width:46rem;margin:0 auto;padding:32px 20px 64px}
h1{font-size:1.7rem;line-height:1.2}ul{padding:0;list-style:none}li{padding:8px 0;border-top:1px solid #0001}li span{color:#5a6b7d;font-size:14px;margin-left:6px}
a{color:#0b5fa5}.note{font-size:14px;color:#5a6b7d}</style></head><body><main>
<p><a href="../index.html">Emory Lab Atlas</a> &rsaquo; <a href="index.html">Departments</a></p>
<h1>%s</h1><p>%s</p>
<p><a href="../index.html#directory">Search and filter these labs in the atlas</a></p>
<ul>%s</ul>
<p class="note">Settings are predicted from paper titles and grants, not recorded, and about 1 in 12 is wrong. Lab Atlas is an independent student project, not an official Emory University service.</p>
</main></body></html>''' % (html.escape(title), html.escape(summary),
            ('<link rel="canonical" href="%sdepartments/%s.html">' % (base, s)) if base else '', html.escape(title), html.escape(summary), rows)
        open(os.path.join(a.out, 'departments', s + '.html'), 'w', encoding='utf-8').write(doc)
        pages.append((s, name, inst, len(people)))
    idx = ''.join('<li><a href="%s.html">%s</a> <span>%s &middot; %d</span></li>' % (s, html.escape(n), html.escape(i), c) for s, n, i, c in sorted(pages, key=lambda x: (x[2], x[1])))
    open(os.path.join(a.out, 'departments', 'index.html'), 'w', encoding='utf-8').write(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Emory research departments and centers: Lab Atlas</title><meta name="description" content="Every Emory department and center in Lab Atlas, with how many of its investigators work at the bench or at a computer.">'
        '<style>body{margin:0;font:16px/1.55 system-ui,sans-serif;color:#031b36;background:#fdffee}main{max-width:46rem;margin:0 auto;padding:32px 20px}li{padding:4px 0}li span{color:#5a6b7d;font-size:14px}</style>'
        '</head><body><main><p><a href="../index.html">Emory Lab Atlas</a></p><h1>Departments and centers</h1><ul>%s</ul></main></body></html>' % idx)

    # 4. sitemap, robots, share image
    urls = [''] + ['departments/index.html'] + ['departments/%s.html' % s for s, *_ in pages]
    if base:
        open(os.path.join(a.out, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
            ''.join('  <url><loc>%s%s</loc></url>\n' % (base, u) for u in urls) + '</urlset>\n')
        open(os.path.join(a.out, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n' % base)
    else:
        open(os.path.join(a.out, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n')
    if os.path.exists(a.og_image): shutil.copy(a.og_image, os.path.join(a.out, 'og-image.png'))

    size = lambda p: os.path.getsize(os.path.join(a.out, p))
    print('index.html %.0f KB, data %.1f MB, app %.0f KB, %d department pages' % (
        size('index.html')/1024, (size('data/atlas.json') + size('data/surehist.json'))/1e6,
        sum(size(f) for f in files)/1024, len(pages)), file=sys.stderr)

if __name__ == '__main__':
    main()
