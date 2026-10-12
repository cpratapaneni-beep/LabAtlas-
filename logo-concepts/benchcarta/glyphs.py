"""Benchcarta glyphs drawn to the conventions of the YC Fall 2026 batch: one heavy, flat glyph on a
black or white square, legible at 16 px. The only colour is the three-dot nucleus from the original
logo (coral, purple, blue), carried over from the atom mark. 100-unit grid.

Usage: python3 glyphs.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))

INK, BG = "var(--ink)", "var(--bg)"
C1, C2, C3 = "var(--c1)", "var(--c2)", "var(--c3)"    # coral, purple, blue
def P(d, c=INK, extra=""): return f'<path d="{d}" style="fill:{c}" {extra}/>'
def L(d, c=INK, w=10, cap="butt", join="miter", extra=""):
    return f'<path d="{d}" fill="none" style="stroke:{c}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="{join}" {extra}/>'
def C(cx, cy, r, c=INK, extra="", stroke=None, sw=0):
    st = f"fill:{c}" + (f";stroke:{stroke}" if stroke else "")
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r}" style="{st}" {f'stroke-width="{sw}"' if stroke else ""} {extra}/>'
def RING(cx, cy, r, w, c=INK): return C(cx, cy, r, "none", stroke=c, sw=w)
def E(cx, cy, rx, ry, rot, c=INK, w=5):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx} {cy})" fill="none" style="stroke:{c}" stroke-width="{w}"/>'
def mask(mid, cut):
    return f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><rect width="100" height="100" fill="#fff"/>{cut}</mask>'
def arc(cx, cy, r, a0, a1):
    p0 = (cx + r*math.cos(math.radians(a0)), cy + r*math.sin(math.radians(a0)))
    p1 = (cx + r*math.cos(math.radians(a1)), cy + r*math.sin(math.radians(a1)))
    return f"M{p0[0]:.2f} {p0[1]:.2f}A{r} {r} 0 {1 if (a1 - a0) % 360 > 180 else 0} 1 {p1[0]:.2f} {p1[1]:.2f}"

def nucleus(cx, cy, d, r, ring=None):
    """The three dots clustered: purple top, coral lower left, blue lower right, each with a fine
    outline in `ring` (the colour behind them) so the overlaps read."""
    ring = ring or BG
    out = ""
    for a, c in ((270, C2), (150, C1), (30, C3)):
        out += C(cx + d*math.cos(math.radians(a)), cy + d*math.sin(math.radians(a)), r, c, stroke=ring, sw=f"{max(.9, r*.18):.2f}")
    return out

M = []
def glyph(name, note, svg): M.append(dict(n=len(M)+1, name=name, note=note, svg=svg))

# 1 Bold atom
glyph("Atom", "The Benchcarta atom at app-icon weight: a heavy ring and three bold orbits 60° apart, with the three-dot nucleus as the only colour.",
      RING(50, 50, 40, 9) + "".join(E(50, 50, 33, 11, t, w=5) for t in (30, 90, 150)) + nucleus(50, 50, 3.9, 3.8))

# 2 Knockout atom
glyph("Knockout Atom", "A solid globe with the orbits cut through it as negative space, a stencil in the way of Simantic and isoquant. The nucleus sits in a clear hole at the centre.",
      mask("@@k", "".join(f'<ellipse cx="50" cy="50" rx="35" ry="12" transform="rotate({t} 50 50)" fill="none" stroke="#000" stroke-width="4.6"/>' for t in (30, 90, 150)) + '<circle cx="50" cy="50" r="12" fill="#000"/>') +
      C(50, 50, 44, extra='mask="url(#@@k)"') + nucleus(50, 50, 4.6, 4.4))

# 3 Flask globe
FG = 22; fr = 33; fy = 61
nx = fr*math.sin(math.radians(FG)); ty = fy - fr*math.cos(math.radians(FG))
glyph("Flask", "The Open Globe turned upright: a round-bottom flask with a heavy neck and lip, holding the three-dot nucleus like a sample. The globe and the lab glass are one shape.",
      L(arc(50, fy, fr, -90 + FG, 270 - FG), w=9) + L(f"M{50 - nx:.2f} {ty:.2f}V12M{50 + nx:.2f} {ty:.2f}V12", w=9) + L(f"M{50 - nx - 8:.2f} 12H{50 + nx + 8:.2f}", w=9) + nucleus(50, fy + 2, 6.2, 6))

# 4 Flask knockout
glyph("Solid Flask", "The flask as one solid silhouette, with the nucleus set in a hole cut through the bulb. It's the boldest version for small sizes.",
      mask("@@f", '<circle cx="50" cy="63" r="13.5" fill="#000"/>') +
      P("M40 8H60V15H57V33.6A33 33 0 1 1 43 33.6V15H40Z", extra='mask="url(#@@f)"') + nucleus(50, 63, 6, 5.8))

# 5 Open C
glyph("Open C", "The Open Globe as a heavy C, the initial of carta, with the three dots leaving through the opening and growing as they go, where the equator once ran out to a point.",
      L(arc(44, 50, 34, 42, 318), w=12) + C(50, 50, 4.2, C1) + C(66, 50, 5.4, C2) + C(84, 50, 6.8, C3))

# 6 Hemisphere B
glyph("Hemisphere B", "The B whose bowls are two hemispheres, at full weight. The lower bowl holds the nucleus. It's the most typographic glyph in the set.",
      L("M24 6V94", w=10) + RING(43, 28.5, 19, 9) + RING(50.5, 68, 26, 9) + L("M43 9.5V47.5", w=4) + nucleus(51, 69, 5.2, 5))

# 7 bc
glyph("bc", "A lowercase b and c set heavy and overlapping, with the nucleus in the b's bowl. Bench and carta in two letters, close to Roma and Hesper in the batch.",
      L("M18 8V84", w=10) + RING(37, 64, 19, 10) + L(arc(66, 64, 19, 45, 315), w=10) + nucleus(37, 64, 4.3, 4.2))

# 8 Single orbit
glyph("One Orbit", "The quietest version: one bold, tilted orbit around a large nucleus. It's the atom reduced to its gesture, in the restraint of Silica and Maritime.",
      E(50, 50, 44, 15, -30, w=9) + nucleus(50, 50, 8.4, 8.2))

# 9 Compass atom
glyph("Compass", "A heavy ring with a north pointer above it and the nucleus at its centre. It's the compass bezel distilled to two parts.",
      RING(50, 54, 36, 10) + P("M50 2L58 14H42Z") + nucleus(50, 54, 7.4, 7.2))

# 10 Bezel disc
ticks = ""
for i in range(24):
    a = -90 + i*15
    if i == 0: continue
    r0, r1 = 37, 37 + (7 if i % 6 == 0 else 4)
    ticks += f"M{50 + r0*math.cos(math.radians(a)):.2f} {50 + r0*math.sin(math.radians(a)):.2f}L{50 + r1*math.cos(math.radians(a)):.2f} {50 + r1*math.sin(math.radians(a)):.2f}"
glyph("Bezel", "A solid globe inside a ring of compass ticks, with a north pointer and the nucleus on the dark face. It's the closest glyph to the full Benchcarta mark.",
      C(50, 50, 31) + L(ticks, w=3) + P("M50 4L56 12.5H44Z") + nucleus(50, 50, 6.6, 6.4, ring=INK))

# 11 Bench globe
glyph("Bench Globe", "The world resting on a lab bench, in two solid shapes, with the nucleus on the globe. It's the most literal reading of the name.",
      C(50, 38, 27) + P("M8 70H92V79H8Z") + P("M17 79H26V94H17ZM74 79H83V94H74Z") + nucleus(50, 38, 6.4, 6.2, ring=INK))

# 12 Pin
glyph("Pin", "A solid map pin whose head is cut open to show the nucleus inside: the place on the map where the science is.",
      mask("@@p", '<circle cx="50" cy="39" r="17" fill="#000"/>') +
      P("M50 96C38 78 15 60 15 39A35 35 0 0 1 85 39C85 60 62 78 50 96Z", extra='mask="url(#@@p)"') + nucleus(50, 39, 7, 6.8))

# 13 Bitmap atom
cells = ""
for gy in range(11):
    for gx in range(11):
        x, y = 5 + gx*8.2, 5 + gy*8.2
        dd = math.hypot(x + 4.1 - 50, y + 4.1 - 50)
        if 33 <= dd <= 45: cells += f'<rect x="{x:.1f}" y="{y:.1f}" width="7.4" height="7.4" style="fill:{INK}"/>'
for gx, gy in ((2, 7), (3, 6), (4, 5), (6, 5), (7, 4), (8, 3), (5, 2), (5, 8)):
    pass
orbit = [(3, 3), (4, 4), (6, 6), (7, 7), (7, 3), (6, 4), (4, 6), (3, 7)]
cells += "".join(f'<rect x="{5 + gx*8.2:.1f}" y="{5 + gy*8.2:.1f}" width="7.4" height="7.4" style="fill:{INK}"/>' for gx, gy in orbit)
cells += "".join(f'<rect x="{5 + gx*8.2:.1f}" y="{5 + gy*8.2:.1f}" width="7.4" height="7.4" style="fill:{c}"/>' for (gx, gy), c in (((5, 4), C2), ((4, 5), C1), ((6, 5), C3)))
glyph("Bitmap Atom", "The atom in 8-unit pixels: a ring, two crossing orbits and a three-pixel nucleus in the brand colours. It belongs to the batch's pixel-mark trend and stays perfectly sharp at 16 px.", cells)

# ---------------------------------------------------------------- page
GROUNDS = [("black", "#0c0c0c", "#ffffff", ("#e0705a", "#c9a2f2", "#5fa8de")),
           ("white", "#ffffff", "#0c0c0c", ("#cf5f49", "#a98ad4", "#3b8ccc")),
           ("navy", "#031b36", "#fdffee", ("#e0705a", "#c9a2f2", "#5fa8de"))]

def tok(bg, ink, cs): return f"--bg:{bg};--ink:{ink};--c1:{cs[0]};--c2:{cs[1]};--c3:{cs[2]}"
def svg(g, size, key): return f'<svg viewBox="0 0 100 100" width="{size}" height="{size}" aria-hidden="true">{g["svg"].replace("@@", f"b{key}-")}</svg>'

CSS = """
/* Layout: a contact sheet, one card per glyph on black, white and navy tiles. */
:root{--page:#f3f3f1;--surface:#ffffff;--fg:#111;--fg2:#5d5d5a;--rule:#e2e2de;
  --sans:'Atlas Text',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--page:#0d0d0d;--surface:#161616;--fg:#f1f1ee;--fg2:#a2a29d;--rule:#2a2a28;color-scheme:dark}}
:root[data-theme="dark"]{--page:#0d0d0d;--surface:#161616;--fg:#f1f1ee;--fg2:#a2a29d;--rule:#2a2a28;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--page);color:var(--fg);font-family:var(--sans);font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-inline:clamp(16px,4vw,40px);padding-block:44px 72px}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--fg2);margin:0 0 10px}
h1{font-weight:500;font-size:clamp(34px,5vw,56px);letter-spacing:-.03em;line-height:1.02;margin:0 0 14px;text-wrap:balance}
.lede{color:var(--fg2);max-width:66ch;margin:0}
.sheet{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;margin:26px 0 8px}
.sheet .t{aspect-ratio:1/1;display:grid;place-items:center;background:var(--bg);border-radius:8px}
.sheet .t svg{width:64%;height:64%}
.rows{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:18px;padding-top:24px}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;min-width:0}
.tiles{display:grid;grid-template-columns:repeat(3,1fr)}
.tile{aspect-ratio:1/1;max-width:100%;display:grid;place-items:center;background:var(--bg)}
.tile svg{width:62%;height:62%}
.meta{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}
.row{display:flex;align-items:baseline;gap:10px;justify-content:space-between}
.no{color:var(--fg2);font-variant-numeric:tabular-nums;font-size:13px}
h3{margin:0;font-weight:500;font-size:17px;letter-spacing:-.01em}
.note{margin:0;color:var(--fg2);font-size:13.5px;flex:1}
.small{display:flex;gap:6px;align-items:center}
.chip{display:grid;place-items:center;background:var(--bg);border-radius:7px}
.c32{width:32px;height:32px}.c16{width:16px;height:16px;border-radius:4px}
.c32 svg{width:24px;height:24px}.c16 svg{width:12px;height:12px}
.lock{display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--bg);color:var(--ink);border-top:1px solid var(--rule)}
.lock b{font-weight:500;font-size:17px;letter-spacing:-.02em}
"""

def page(fonts, full_doc):
    sheet = "".join(f'<div class="t" style="{tok(*GROUNDS[0][1:3], GROUNDS[0][3])}">{svg(g, 120, f"s{g["n"]}")}</div>' for g in M)
    cards = ""
    for g in M:
        tiles = "".join(f'<div class="tile" style="{tok(bg, ink, cs)}">{svg(g, 200, f"{g["n"]}{k}")}</div>' for k, bg, ink, cs in GROUNDS)
        chips = "".join(f'<span class="chip c32" style="{tok(bg, ink, cs)}">{svg(g, 24, f"{g["n"]}{k}s")}</span>' for k, bg, ink, cs in GROUNDS[:2]) + \
                "".join(f'<span class="chip c16" style="{tok(bg, ink, cs)}">{svg(g, 12, f"{g["n"]}{k}t")}</span>' for k, bg, ink, cs in GROUNDS[:2])
        k, bg, ink, cs = GROUNDS[0]
        cards += f'''<article class="card"><div class="tiles">{tiles}</div><div class="meta">
  <div class="row"><h3><span class="no">{g["n"]:02d}</span>&nbsp; {html.escape(g["name"])}</h3><span class="small" title="32 and 16 px">{chips}</span></div>
  <p class="note">{html.escape(g["note"])}</p></div>
  <div class="lock" style="{tok(bg, ink, cs)}">{svg(g, 26, f"{g["n"]}lk")}<b>Benchcarta</b></div></article>\n'''
    body = f'''<div class="wrap">
  <p class="eyebrow">Benchcarta · glyphs</p>
  <h1>Benchcarta, one bold glyph</h1>
  <p class="lede">Thirteen glyphs drawn to the conventions of the YC Fall 2026 batch: one heavy, flat shape on a black or white square, legible at 16 px. They're built from the ideas you've picked along the way: the atom and its orbits, the three-dot nucleus, the open globe and flask, the compass bezel, the Hemisphere B and the bench. The three dots, in coral, purple and blue, are the only colour.</p>
  <div class="sheet">{sheet}</div>
  <main class="rows">{cards}</main>
</div>'''
    head = f'<title>Benchcarta Glyphs</title>\n<style>\n{fonts}\n{CSS}\n</style>'
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

def export():
    out = os.path.join(HERE, "svg-glyphs"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for g in M:
        for k, bg, ink, cs in GROUNDS[:2]:
            body = g["svg"].replace("@@", "y").replace(INK, ink).replace(BG, bg).replace(C1, cs[0]).replace(C2, cs[1]).replace(C3, cs[2])
            body = re.sub(r'style="fill:([^;"]+);stroke:([^"]+)"', r'fill="\1" stroke="\2"', body)
            body = re.sub(r'style="(fill|stroke):([^"]+)"', r'\1="\2"', body)
            slug = re.sub(r"[^a-z0-9]+", "-", g["name"].lower()).strip("-")
            open(os.path.join(out, f"{g['n']:02d}-{slug}-{k}.svg"), "w").write(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="512" height="512"><rect width="100" height="100" fill="{bg}"/><g transform="translate(18 18) scale(.64)">{body}</g></svg>\n')

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "glyphs.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built", len(M))
