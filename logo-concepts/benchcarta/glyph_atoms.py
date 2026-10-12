"""Benchcarta: the Atom and Knockout Atom glyphs with thinner lines and a compass bezel.

Usage: python3 glyph_atoms.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("gl", os.path.join(HERE, "glyphs.py"))
G = importlib.util.module_from_spec(spec); argv = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(G); sys.argv = argv
INK, BG, P, L, C, RING, mask, nucleus, GROUNDS, tok = G.INK, G.BG, G.P, G.L, G.C, G.RING, G.mask, G.nucleus, G.GROUNDS, G.tok

def bezel(r0=38, short=3.5, long=6.5, w=2.2):
    """Compass ticks every 15 degrees from radius r0, long at the quarters, and a solid north pointer."""
    d = ""
    for i in range(1, 24):
        a = -90 + i*15; L_ = long if i % 6 == 0 else short
        d += f"M{50 + r0*math.cos(math.radians(a)):.2f} {50 + r0*math.sin(math.radians(a)):.2f}L{50 + (r0 + L_)*math.cos(math.radians(a)):.2f} {50 + (r0 + L_)*math.sin(math.radians(a)):.2f}"
    return L(d, w=w) + P(f"M50 {50 - r0:.1f}L44.5 {50 - r0 - 8.5:.1f}H55.5Z")

ORB = (30, 90, 150)
M = []
def glyph(name, note, full, small): M.append(dict(n=len(M)+1, name=name, note=note, full=full, small=small))

# 1 Atom: thin ring, thin orbits, nucleus, compass bezel
glyph("Atom",
      "The atom glyph with its lines thinned: the globe ring at 4.5 and the orbits at 2.6, down from 9 and 5. A compass bezel sits outside the ring, with a tick every 15°, longer ones at the quarters and a solid pointer at north.",
      RING(50, 50, 32, 4.5) + "".join(G.E(50, 50, 27, 9, t, w=2.6) for t in ORB) + nucleus(50, 50, 3.4, 3.3) + bezel(),
      RING(50, 50, 42, 7) + "".join(G.E(50, 50, 35, 12, t, w=4.4) for t in ORB) + nucleus(50, 50, 4.6, 4.5))

# 2 Knockout atom: solid globe with thin orbit cuts, nucleus in a clear centre, compass bezel
glyph("Knockout Atom",
      "The solid globe with its orbits cut through it, now as fine 2.4 lines instead of 4.6, and a smaller clear centre for the nucleus. The same compass bezel rings it.",
      mask("@@k", "".join(f'<ellipse cx="50" cy="50" rx="27" ry="9" transform="rotate({t} 50 50)" fill="none" stroke="#000" stroke-width="2.4"/>' for t in ORB) + '<circle cx="50" cy="50" r="8.6" fill="#000"/>') +
      C(50, 50, 33, extra='mask="url(#@@k)"') + nucleus(50, 50, 3.4, 3.3) + bezel(),
      mask("@@s", "".join(f'<ellipse cx="50" cy="50" rx="36" ry="12" transform="rotate({t} 50 50)" fill="none" stroke="#000" stroke-width="3.6"/>' for t in ORB) + '<circle cx="50" cy="50" r="11.5" fill="#000"/>') +
      C(50, 50, 44, extra='mask="url(#@@s)"') + nucleus(50, 50, 4.6, 4.5))

def svg(body, size, key): return f'<svg viewBox="0 0 100 100" width="{size}" height="{size}" aria-hidden="true">{body.replace("@@", f"a{key}-")}</svg>'

CSS = G.CSS + """
.hero2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:26px 0 6px}
.hero2 .t{aspect-ratio:1/1;display:grid;place-items:center;background:var(--bg);border-radius:12px}
.hero2 .t svg{width:66%;height:66%}
.apps{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end;padding:12px 14px 14px;border-top:1px solid var(--rule)}
.apps figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:6px;font-size:11px;color:var(--fg2)}
.app{display:grid;place-items:center;background:var(--bg)}
@media (max-width:700px){.hero2{grid-template-columns:minmax(0,1fr)}}
"""

def page(fonts, full_doc):
    k0 = GROUNDS[0]
    hero = "".join(f'<div class="t" style="{tok(k0[1], k0[2], k0[3])}">{svg(g["full"], 400, f"h{g["n"]}")}</div>' for g in M)
    cards = ""
    for g in M:
        tiles = "".join(f'<div class="tile" style="{tok(bg, ink, cs)}">{svg(g["full"], 200, f"{g["n"]}{k}")}</div>' for k, bg, ink, cs in GROUNDS)
        b, w = GROUNDS[0], GROUNDS[1]
        apps = (f'<figure><span class="app" style="{tok(b[1], b[2], b[3])};width:88px;height:88px;border-radius:20px">{svg(g["full"], 76, f"{g["n"]}a1")}</span>App icon</figure>'
                f'<figure><span class="app" style="{tok(w[1], w[2], w[3])};width:88px;height:88px;border-radius:20px;box-shadow:inset 0 0 0 1px var(--rule)">{svg(g["full"], 76, f"{g["n"]}a2")}</span>Light</figure>'
                f'<figure><span class="app" style="{tok(b[1], b[2], b[3])};width:48px;height:48px;border-radius:11px">{svg(g["full"], 42, f"{g["n"]}a3")}</span>48 px</figure>'
                f'<figure><span class="app" style="{tok(b[1], b[2], b[3])};width:32px;height:32px;border-radius:7px">{svg(g["small"], 28, f"{g["n"]}a4")}</span>32 px, small</figure>'
                f'<figure><span class="app" style="{tok(b[1], b[2], b[3])};width:16px;height:16px;border-radius:4px">{svg(g["small"], 15, f"{g["n"]}a5")}</span>16 px, small</figure>'
                f'<figure><span class="app" style="{tok(w[1], w[2], w[3])};width:16px;height:16px;border-radius:4px;box-shadow:inset 0 0 0 1px var(--rule)">{svg(g["small"], 15, f"{g["n"]}a6")}</span>16 px light</figure>')
        cards += f'''<article class="card"><div class="tiles">{tiles}</div><div class="meta">
  <div class="row"><h3><span class="no">{g["n"]:02d}</span>&nbsp; {html.escape(g["name"])}</h3></div>
  <p class="note">{html.escape(g["note"])}</p></div>
  <div class="apps">{apps}</div>
  <div class="lock" style="{tok(b[1], b[2], b[3])}">{svg(g["full"], 30, f"{g["n"]}lk")}<b>Benchcarta</b></div>
  <div class="lock" style="{tok(w[1], w[2], w[3])}">{svg(g["full"], 30, f"{g["n"]}lw")}<b>Benchcarta</b></div></article>\n'''
    body = f'''<div class="wrap">
  <p class="eyebrow">Benchcarta · glyphs, round two</p>
  <h1>Atom and Knockout Atom, with a bezel</h1>
  <p class="lede">The two glyphs you picked, with thinner lines and the compass bezel added: a tick every 15°, longer ticks at the quarters, and a solid pointer at north. The globe shrinks a little to make room for the bezel. At 32 px and below each falls back to a simplified version without the bezel, because the ticks blur into noise at that size.</p>
  <div class="hero2">{hero}</div>
  <main class="rows" style="grid-template-columns:repeat(auto-fill,minmax(420px,1fr))">{cards}</main>
</div>'''
    head = f'<title>Benchcarta Atom Glyphs</title>\n<style>\n{fonts}\n{CSS}\n</style>'
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

def export():
    out = os.path.join(HERE, "svg-glyph-atoms"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for g in M:
        slug = re.sub(r"[^a-z0-9]+", "-", g["name"].lower()).strip("-")
        for kind in ("full", "small"):
            for k, bg, ink, cs in GROUNDS[:2]:
                body = g[kind].replace("@@", "y").replace(INK, ink).replace(BG, bg).replace(G.C1, cs[0]).replace(G.C2, cs[1]).replace(G.C3, cs[2])
                body = re.sub(r'style="fill:([^;"]+);stroke:([^"]+)"', r'fill="\1" stroke="\2"', body)
                body = re.sub(r'style="(fill|stroke):([^"]+)"', r'\1="\2"', body)
                open(os.path.join(out, f"{g['n']:02d}-{slug}-{k}{'' if kind == 'full' else '-small'}.svg"), "w").write(
                    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="512" height="512"><rect width="100" height="100" fill="{bg}"/><g transform="translate(12 12) scale(.76)">{body}</g></svg>\n')

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "glyph-atoms.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built", len(M))
