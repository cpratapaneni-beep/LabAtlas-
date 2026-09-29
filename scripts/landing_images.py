"""Put photographs into the landing page's image slots.

The landing page has one slot per photograph, named in PHOTOS.landing in the
page's script (hero-1, view-atlas, note-method, ...). An empty slot shows its
label and the size it wants. This fills slots from a folder of image files named
after them, embedding each as a data URI so the atlas stays one self-contained
file.

  python3 scripts/landing_images.py atlas.html --list
  python3 scripts/landing_images.py atlas.html photos/ -o atlas_with_photos.html

A file called hero-1.jpg (or .jpeg, .png, .webp, .avif) fills the hero-1 slot.
Files whose names match no slot are reported and skipped; slots with no file
keep whatever they already hold.
"""
import argparse, base64, mimetypes, os, re, sys

EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.avif'}
LARGE = 1_500_000


def landing_block(html):
    i = html.find('const PHOTOS = {')
    if i < 0:
        sys.exit('no PHOTOS block in this file - is it an atlas page?')
    j = html.find('landing: {', i)
    if j < 0:
        sys.exit('this atlas has no landing slots (it predates v83)')
    k = html.index('}', j)
    return j, k


def slots(block):
    return re.findall(r"'([a-z0-9-]+)':\s*'([^']*)',?\s*//\s*(.*)", block)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('html')
    ap.add_argument('folder', nargs='?')
    ap.add_argument('-o', '--out')
    ap.add_argument('--list', action='store_true', help='print the slots and the size each one wants')
    a = ap.parse_args()
    html = open(a.html, encoding='utf-8').read()
    j, k = landing_block(html)
    block = html[j:k]
    have = slots(block)
    if a.list or not a.folder:
        for key, val, note in have:
            print('%-14s %-7s %s' % (key, 'filled' if val else 'empty', note.strip()))
        return
    if not a.out:
        sys.exit('say where to write the result with -o (the source is never overwritten)')
    names = {key for key, _, _ in have}
    done = []
    for fn in sorted(os.listdir(a.folder)):
        key, ext = os.path.splitext(fn)
        if ext.lower() not in EXTS:
            continue
        if key not in names:
            print('skipped %s: no slot called %s' % (fn, key))
            continue
        raw = open(os.path.join(a.folder, fn), 'rb').read()
        if len(raw) > LARGE:
            print('note: %s is %.1f MB; the slot is drawn at the size in --list, so it could be smaller'
                  % (fn, len(raw) / 1e6))
        mime = mimetypes.guess_type(fn)[0] or 'image/jpeg'
        uri = 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode())
        block = re.sub(r"('%s':\s*)'[^']*'" % re.escape(key), lambda m: m.group(1) + "'" + uri + "'", block, count=1)
        done.append(key)
    open(a.out, 'w', encoding='utf-8').write(html[:j] + block + html[k:])
    print('filled %d slot(s): %s' % (len(done), ', '.join(done) or 'none'))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
