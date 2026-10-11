"""Lab Atlas marks drawn to the conventions of the YC Fall 2026 batch: one heavy, flat glyph,
monochrome plus at most one accent, legible at 16 px. All marks sit on a 100-unit grid.

Usage: python3 build.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))

INK, ACC, BG = "var(--ink)", "var(--acc)", "var(--bg)"
def P(d, c=INK, extra=""): return f'<path d="{d}" style="fill:{c}" {extra}/>'
def L(d, c=INK, w=10, cap="butt", join="miter", extra=""):
    return f'<path d="{d}" fill="none" style="stroke:{c}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="{join}" {extra}/>'
def C(cx, cy, r, c=INK, extra=""): return f'<circle cx="{cx}" cy="{cy}" r="{r}" style="fill:{c}" {extra}/>'
def mask(mid, cut):  # white keeps, black cuts
    return f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><rect width="100" height="100" fill="#fff"/>{cut}</mask>'

def q_x_at_y(p0, p1, p2, y):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        t = (lo + hi)/2
        yt = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]
        if (yt < y) == (p2[1] > p0[1]): lo = t
        else: hi = t
    t = (lo + hi)/2
    return (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0]

M = []
def mark(name, note, svg): M.append(dict(n=len(M)+1, name=name, note=note, svg=svg))

# 1 Pole A, bold: two meridians meeting at the pole, equator as the crossbar
A0, AL, AR = (50, 12), (25, 40), (75, 40)
lx, rx = q_x_at_y(A0, AL, (22, 88), 62), q_x_at_y(A0, AR, (78, 88), 62)
mark("Pole A", "Pole A at full weight: two meridians meet in a sharp point at the north pole, and the equator is a single accent bar. Nothing else.",
     L("M22 88Q25 40 50 12Q75 40 78 88", w=13) + L(f"M{lx+4:.1f} 62Q50 69 {rx-4:.1f} 62", ACC, 10))

# 2 Knockout: a solid globe with the A cut out of it
mark("Knockout Globe", "A solid sphere with Pole A cut clean through it as negative space. It's a stencil, in the way of Simantic and isoquant in the batch.",
     mask("@@k", L("M24 92Q27 44 50 6Q73 44 76 92", "#000", 9) + L("M28 60Q50 68 72 60", "#000", 8)) +
     C(50, 50, 42, extra='mask="url(#@@k)"') + C(50, 9.5, 4.2, ACC))

# 3 Pixel globe with an A
px = []
for gy in range(10):
    for gx in range(10):
        x, y = gx*9 + 5, gy*9 + 5
        if math.hypot(x + 4.5 - 50, y + 4.5 - 50) <= 44: px.append((gx, gy))
A_cells = {(4, 1), (5, 1), (3, 2), (6, 2), (3, 3), (6, 3), (2, 4), (7, 4), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (2, 6), (7, 6), (1, 7), (8, 7), (1, 8), (8, 8)}
mark("Bitmap Globe", "A globe drawn in 9-unit pixels with the A left out of the grid as negative space, and two accent pixels at the pole. It belongs to the batch's pixel-mark trend (Cyclon, Grep, Kailash) and stays sharp at 16 px.",
     "".join(f'<rect x="{gx*9+5}" y="{gy*9+5}" width="8.2" height="8.2" style="fill:{ACC if (gx, gy) == (4, 0) or (gx, gy) == (5, 0) else INK}"/>' for gx, gy in px if (gx, gy) not in A_cells))

# 4 North star A: a four-point star whose north point is notched into an A
star = "M50 4L60 40L96 50L60 60L50 96L40 60L4 50L40 40Z"
mark("North Star A", "A four-point compass star whose north point is cut with a crossbar notch, so the top of the star is an A. Navigation and the initial in one shape.",
     mask("@@n", P("M50 22L56 40H44Z", "#000") + L("M43 33H57", "#000", 3.4)) + P(star, extra='mask="url(#@@n)"') + C(50, 50, 5.5, ACC))

# 5 LA blocks: heavy geometric L and A that share a baseline
mark("LA Blocks", "L and A as two heavy geometric blocks: a solid L and a solid triangle with its counter cut. They share a baseline and the A has an accent square, much as Roma and Mantle use one bright shape.",
     P("M8 14H26V70H48V88H8Z") + mask("@@b", P("M66 52L72 70H60Z", "#000")) + P("M50 88L71 14L92 88Z", extra='mask="url(#@@b)"') + f'<rect x="64" y="74" width="14" height="14" style="fill:{ACC}"/>')

# 6 Single-line LA, heavy
mark("One Stroke", "L into A in one heavy, unbroken stroke with square ends, like Keres or Hesper. The A's crossbar is the only accent.",
     L("M14 12V86H40L58 14L78 86", w=12) + L("M47 60H70", ACC, 9))

# 7 Atlas arch: an abstract titan, a circle carried on an arch of shoulders
mark("Titan", "Atlas reduced to two shapes: a sphere carried on an arch of shoulders and raised arms. This is the batch's heavy rounded geometry, in the manner of Capveon and Lyon. It's the titan without the illustration.",
     C(50, 34, 24, ACC) + P("M10 92C10 62 26 50 38 50C42 50 44 54 44 58V64H56V58C56 54 58 50 62 50C74 50 90 62 90 92Z") +
     L("M20 66C14 52 16 36 26 26M80 66C86 52 84 36 74 26", w=9, cap="round"))

# 8 Pin A
mark("Pin A", "A map pin whose head is cut with a solid A. It marks where a lab is, and the cut-out A doubles as the pin's eye.",
     mask("@@p", P("M50 16L62 50H38Z", "#000") + C(50, 50, 0)) + P("M50 96C38 78 16 60 16 38A34 34 0 0 1 84 38C84 60 62 78 50 96Z", extra='mask="url(#@@p)"') +
     mask("@@q", P("M46 40H54V46H46Z", "#000")) + P("M50 22L60 50H40Z", BG) + P("M47.2 41H52.8L54.2 45.5H45.8Z", INK) + C(50, 70, 4, ACC))

# 9 Curved grid: a 3x3 cell of the graticule with one cell lit
g = ""
for i, (a, b) in enumerate([(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]):
    pass
mark("Graticule Cell", "A heavy 3×3 piece of the globe's grid, curved like a sphere, with one cell filled: the lab you were looking for.",
     mask("@@g", "") +
     f'<clipPath id="@@gc"><circle cx="50" cy="50" r="44"/></clipPath>' +
     f'<g clip-path="url(#@@gc)">' + L("M50 6V94M28 8Q10 50 28 92M72 8Q90 50 72 92", w=7) + L("M6 50H94M10 28Q50 38 90 28M10 72Q50 82 90 72", w=7) +
     P("M52.5 52.4L69.4 52.4Q75 62 73 74Q62 76.2 52.5 76.2Z", ACC) + '</g>' + f'<circle cx="50" cy="50" r="40.5" fill="none" style="stroke:{INK}" stroke-width="7"/>')

# 10 Compass ring
mark("Compass", "A heavy compass ring with a north wedge in the accent colour and a centre pin. It's the compass markings you liked, at app-icon weight.",
     f'<circle cx="50" cy="50" r="36" fill="none" style="stroke:{INK}" stroke-width="12"/>' + P("M50 4L60 24H40Z", ACC) +
     P("M50 22L58 50L50 78L42 50Z") + P("M50 22L58 50H42Z", ACC) + C(50, 50, 4, BG))

# 11 Lens globe
mark("Lens", "A magnifier whose lens is a globe: search across the atlas. The meridians inside the lens form a small A.",
     f'<circle cx="42" cy="42" r="30" fill="none" style="stroke:{INK}" stroke-width="10"/>' + L("M64 64L90 90", w=14) +
     L("M27 62Q29 38 42 22Q55 38 57 62", ACC, 6) + L("M32 48H52", ACC, 5))

# 12 Folded A: a three-panel folded map whose middle crease peaks into an A
mark("Folded Map", "A folded map seen edge-on: three panels, with the middle fold rising to an accent peak. The whole shape can read as an M, so it's the weakest A in the set.",
     P("M6 88L28 24L38 52L16 88Z") + P("M38 52L50 14L62 52L56 70H44Z", ACC) + P("M62 52L72 24L94 88H84Z") + L("M40 70H60", INK, 0))

# 13 Latitude bars: a sphere built from stripes, with an A cut through them
bars = "".join(f'<rect x="0" y="{y}" width="100" height="7" style="fill:{INK}"/>' for y in range(8, 92, 11))
mark("Latitude Bars", "A sphere made of eight latitude bars, with a solid accent A standing through the stack. Stripes show up in the batch too (Hue, Ignition Benefits).",
     mask("@@l", P("M50 14L74 92H62L50 52L38 92H26Z", "#000")) + f'<clipPath id="@@lc"><circle cx="50" cy="50" r="44"/></clipPath>' +
     f'<g clip-path="url(#@@lc)" mask="url(#@@l)">{bars}</g>' + P("M50 14L74 92H62L50 52L38 92H26Z", ACC))

# 14 Pole star globe
mark("Pole Star", "A solid globe with an accent four-point star at its north pole, sitting on the rim. It's the simplest globe in the set, and the star does all the work.",
     mask("@@s", L("M50 24Q30 46 30 92M50 24Q70 46 70 92", "#000", 4.5) + L("M8 62Q50 72 92 62", "#000", 4.5)) +
     C(50, 56, 38, extra='mask="url(#@@s)"') + P("M50 2L55 15L68 20L55 25L50 38L45 25L32 20L45 15Z", ACC))

# 15 Meridian lambda: the lightest mark, one curved meridian A and a pole dot
mark("Meridian Point", "The quietest version: one thin curved A of two meridians and an accent dot at the pole, in the restraint of Silica and Maritime.",
     L("M16 90Q24 44 50 14Q76 44 84 90", w=6, join="round") + C(50, 14, 7, ACC))

# ---------------------------------------------------------------- page
GROUNDS = [("black", "#0c0c0c", "#ffffff"), ("white", "#ffffff", "#0c0c0c"), ("navy", "#031b36", "#fdffee")]
ACCENTS = [("orange", "Signal orange", "#ff5b1f"), ("gold", "Gold", "#e3a92b"), ("mono", "None", None)]

def svg(m, size, key):
    body = m["svg"].replace("@@", f"y{key}-")
    return f'<svg viewBox="0 0 100 100" width="{size}" height="{size}" aria-hidden="true">{body}</svg>'

CSS = """
/* Layout: a contact sheet, one row per mark, each shown on black, white and navy tiles, with an accent switch. */
:root{--page:#f3f3f1;--surface:#ffffff;--fg:#111;--fg2:#5d5d5a;--rule:#e2e2de;--acc:#ff5b1f;
  --sans:'Atlas Text',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--page:#0d0d0d;--surface:#161616;--fg:#f1f1ee;--fg2:#a2a29d;--rule:#2a2a28;color-scheme:dark}}
:root[data-theme="dark"]{--page:#0d0d0d;--surface:#161616;--fg:#f1f1ee;--fg2:#a2a29d;--rule:#2a2a28;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--page);color:var(--fg);font-family:var(--sans);font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-inline:clamp(16px,4vw,40px);padding-block:44px 72px}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--fg2);margin:0 0 10px}
h1{font-weight:500;font-size:clamp(34px,5vw,56px);letter-spacing:-.03em;line-height:1.02;margin:0 0 14px;text-wrap:balance}
.lede{color:var(--fg2);max-width:64ch;margin:0}
.learned{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin:28px 0 8px;padding:20px 0;border-block:1px solid var(--rule)}
.learned b{display:block;font-weight:500;margin-bottom:4px}
.learned p{margin:0;color:var(--fg2);font-size:13.5px}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--page);display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding-block:12px;border-bottom:1px solid var(--rule)}
.bar .lbl{font-size:12px;color:var(--fg2);letter-spacing:.08em;text-transform:uppercase;margin-right:4px}
.bar button{font:inherit;font-size:13px;color:var(--fg);background:transparent;border:1px solid var(--rule);border-radius:999px;padding:6px 12px;cursor:pointer;display:inline-flex;gap:8px;align-items:center}
.bar button i{width:12px;height:12px;border-radius:50%;display:inline-block;box-shadow:inset 0 0 0 1px var(--rule)}
.bar button[aria-pressed="true"]{background:var(--fg);color:var(--page);border-color:var(--fg)}
.bar button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
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
"""

def page(fonts, full_doc):
    cards = ""
    for m in M:
        tiles = "".join(f'<div class="tile" style="--bg:{bg};--ink:{ink}">{svg(m, 200, f"{m["n"]}{k}")}</div>' for k, bg, ink in GROUNDS)
        chips = "".join(f'<span class="chip c32" style="--bg:{bg};--ink:{ink}">{svg(m, 24, f"{m["n"]}{k}s")}</span>' for k, bg, ink in GROUNDS[:2]) + \
                "".join(f'<span class="chip c16" style="--bg:{bg};--ink:{ink}">{svg(m, 12, f"{m["n"]}{k}t")}</span>' for k, bg, ink in GROUNDS[:2])
        cards += f'''<article class="card"><div class="tiles">{tiles}</div><div class="meta">
  <div class="row"><h3><span class="no">{m["n"]:02d}</span>&nbsp; {html.escape(m["name"])}</h3><span class="small" title="32 and 16 px">{chips}</span></div>
  <p class="note">{html.escape(m["note"])}</p></div></article>\n'''
    btns = "".join(f'<button type="button" id="acc-{k}" data-acc="{v or "currentColor"}" aria-pressed="{"true" if i == 0 else "false"}"><i style="background:{v or "transparent"}"></i>{label}</button>' for i, (k, label, v) in enumerate(ACCENTS))
    body = f'''<div class="wrap">
  <p class="eyebrow">Lab Atlas · round eight</p>
  <h1>Bold, flat, one glyph</h1>
  <p class="lede">Fifteen marks drawn to the conventions of the Y Combinator Fall 2026 batch. I looked at all 127 of its logos, and these follow what the strongest ones share. Each is shown on black, white and navy, with a switch for the accent colour.</p>
  <div class="learned">
    <div><b>One heavy glyph</b><p>Nearly every mark is a single flat symbol on a black or white square, with no gradients and no illustration. The few detailed marks in the batch are the weakest at small size.</p></div>
    <div><b>Letters cut from geometry</b><p>K, M, Σ, λ, G and H, and several A's: Silica, Maritime, Vexo, Asakana. Ageospatial already uses an A with a globe, so these avoid that.</p></div>
    <div><b>One accent at most</b><p>Mantle, Roma, Spine and Hesper add a single orange to an otherwise monochrome mark. The rest use no colour at all.</p></div>
    <div><b>Pixels and stencils</b><p>Bitmap marks (Cyclon, Grep, Kailash) and stencil cuts (Simantic, isoquant) are a visible trend. So is heavy rounded geometry (Lyon, Capveon).</p></div>
  </div>
  <div class="bar" role="group" aria-label="Accent colour"><span class="lbl">Accent</span>{btns}</div>
  <main class="rows" id="rows">{cards}</main>
</div>
<script>
(function(){{
  var bs=[].slice.call(document.querySelectorAll('[data-acc]'));
  function set(b){{document.documentElement.style.setProperty('--acc',b.dataset.acc);bs.forEach(function(x){{x.setAttribute('aria-pressed',String(x===b))}});
    try{{localStorage.setItem('la-yc-acc',b.id)}}catch(e){{}}}}
  bs.forEach(function(b){{b.addEventListener('click',function(){{set(b)}})}});
  try{{var s=localStorage.getItem('la-yc-acc');var b=s&&document.getElementById(s);if(b)set(b)}}catch(e){{}}
}})();
</script>'''
    head = f'<title>Lab Atlas Glyphs</title>\n<style>\n{fonts}\n{CSS}\n</style>'
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

def export():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for m in M:
        for k, bg, ink in GROUNDS[:2]:
            body = m["svg"].replace("@@", "y").replace("var(--ink)", ink).replace("var(--acc)", "#ff5b1f").replace("var(--bg)", bg)
            body = re.sub(r'style="(fill|stroke):([^"]+)"', r'\1="\2"', body)
            slug = re.sub(r"[^a-z0-9]+", "-", m["name"].lower()).strip("-")
            open(os.path.join(out, f"{m['n']:02d}-{slug}-{k}.svg"), "w").write(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="512" height="512"><rect width="100" height="100" fill="{bg}"/><g transform="translate(18 18) scale(.64)">{body}</g></svg>\n')

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "index.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built", len(M))
