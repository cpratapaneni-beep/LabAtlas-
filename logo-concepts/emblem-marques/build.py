"""Lab Atlas marques: emblems built only from circles and ellipses, in the tradition of
automotive badges (Audi's interlocking rings, Toyota's ellipses, VW's ringed monogram).
Each mark is rendered flat, as a chrome badge, and as its construction drawing.

Usage: python3 build.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 200, 140

# ---------------------------------------------------------------- geometry
def ellipse_pts(cx, cy, rx, ry, rot=0, n=360):
    a = math.radians(rot); out = []
    for i in range(n):
        t = 2*math.pi*i/n
        x, y = rx*math.cos(t), ry*math.sin(t)
        out.append((cx + x*math.cos(a) - y*math.sin(a), cy + x*math.sin(a) + y*math.cos(a)))
    return out

def d_of(pts, closed=True):
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + ("Z" if closed else "")

def ring_fill(cx, cy, rx, ry, rot, ox, oy, irx, iry):
    """Toyota-style ring: an outer ellipse minus an offset inner ellipse, so the weight varies."""
    return d_of(ellipse_pts(cx, cy, rx, ry, rot)) + d_of(ellipse_pts(cx + ox, cy + oy, irx, iry, rot)[::-1])

def crossings(p, q):
    """Indices along ring p where it crosses ring q (sampled polylines)."""
    out = []
    def seg_x(a, b, c, d):
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
        den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        if abs(den) < 1e-9: return None
        t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4))/den
        u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3))/den
        return (t, u) if 0 <= t <= 1 and 0 <= u <= 1 else None
    n, m = len(p), len(q)
    for i in range(n):
        a, b = p[i], p[(i+1) % n]
        for j in range(m):
            r = seg_x(a, b, q[j], q[(j+1) % m])
            if r: out.append((i, j))
    return out

class Mark:
    def __init__(self, name, idea, view=(0, 0, W, H)):
        self.name, self.idea, self.view = name, idea, view
        self.strokes = []   # (d, width)
        self.fills = []     # d (evenodd)
        self.overs = []     # (d, width) short over-pieces for interlacing
        self.guides = []    # construction svg snippets
        self.dims = []      # (x, y, text) construction labels

    def interlace(self, rings, w, rule, span=9):
        """rings: sampled polylines. rule(i, j, k) -> True if ring i passes over ring j at their k-th crossing
        (crossings counted along ring i, i < j). Each physical crossing is decided once."""
        for r in rings: self.strokes.append((d_of(r), w))
        for i in range(len(rings)):
            for j in range(i + 1, len(rings)):
                for k, (ia, jb) in enumerate(crossings(rings[i], rings[j])):
                    over, idx = (rings[i], ia) if rule(i, j, k) else (rings[j], jb)
                    n = len(over); piece = [over[(idx + s) % n] for s in range(-span, span + 2)]
                    self.overs.append((d_of(piece, False), w))

# ---------------------------------------------------------------- the marques
MARKS = []

def arc_pts(cx, cy, r, a0, a1, n=120):
    return [(cx + r*math.cos(math.radians(a0 + (a1-a0)*i/n)), cy + r*math.sin(math.radians(a0 + (a1-a0)*i/n))) for i in range(n+1)]

def gothic(apex, foot_dx, foot_y, R):
    """Two circular arcs of radius R meeting at the apex: a pointed arch, i.e. an A without its crossbar.
    Returns (left_pts, right_pts, centres)."""
    ax, ay = apex
    out, centres = [], []
    for side in (-1, 1):
        fx = ax + side*foot_dx
        # centre lies on the perpendicular bisector of apex-foot, at distance R from both, on the far side
        mx, my = (ax + fx)/2, (ay + foot_y)/2
        dx, dy = fx - ax, foot_y - ay; L = math.hypot(dx, dy); h = math.sqrt(R*R - (L/2)**2)
        nx, ny = -dy/L, dx/L
        c1 = (mx + nx*h, my + ny*h); c2 = (mx - nx*h, my - ny*h)
        c = c1 if (c1[0] - ax)*side < 0 else c2   # the centre on the opposite side bulges the leg outward
        centres.append(c)
        a0 = math.degrees(math.atan2(ay - c[1], ax - c[0])); a1 = math.degrees(math.atan2(foot_y - c[1], fx - c[0]))
        if abs(a1 - a0) > 180: a1 += 360 if a1 < a0 else -360
        out.append(arc_pts(c[0], c[1], R, a0, a1))
    return out[0], out[1], centres

# 1 Horizon: an ellipse, an A of two arcs whose apex touches the rim, and the equator edge to edge
m = Mark("Horizon", "A wide ellipse holds an A made of two circular arcs. The A's apex touches the top of the rim and its feet stand on the bottom. The equator runs straight across, rim to rim, and serves as the crossbar. The mark reads as two meridians meeting at the pole, or as an A standing on the horizon.")
L1, R1, cs = gothic((100, 12), 40, 123.2, 150)
m.strokes += [(d_of(ellipse_pts(100, 70, 94, 58, 0, 360)), 6), (d_of(L1, False), 6), (d_of(R1, False), 6),
              (f"M{100 - 94*math.sqrt(1 - (16/58)**2):.2f} 86H{100 + 94*math.sqrt(1 - (16/58)**2):.2f}", 6)]
m.guides += ['<ellipse cx="100" cy="70" rx="94" ry="58"/>', '<path d="M100 2V138M2 86H198"/>'] + [f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="150"/>' for c in cs]
m.dims += [(150, 18, "E  94 × 58"), (8, 100, "equator 16 below centre"), (124, 134, "legs  arcs of R 150")]
MARKS.append(m)

# 2 Atlas arch: a pointed arch (the A) holds a globe on its apex
m = Mark("Atlas Arch", "Atlas reduced to geometry. A pointed arch of two circular arcs forms the A, and it carries a globe on its apex the way the titan carries the heavens. The globe is a circle with one meridian and one parallel, and a straight crossbar completes the letter.")
gx, gy, gr = 100, 42, 30
L2, R2, cs2 = gothic((100, gy + gr), 36, 132, 96)
yb = 114
def x_on(pts, y): return min(pts, key=lambda p: abs(p[1] - y))[0]
m.strokes += [(d_of(ellipse_pts(gx, gy, gr, gr, 0, 360)), 6), (d_of(ellipse_pts(gx, gy, 12, gr, 0, 360)), 4),
              (f"M{gx - gr} {gy}A{gr} 9 0 0 0 {gx + gr} {gy}", 4),
              (d_of(L2, False), 6), (d_of(R2, False), 6), (f"M{x_on(L2, yb):.2f} {yb}H{x_on(R2, yb):.2f}", 6)]
m.guides += [f'<circle cx="{gx}" cy="{gy}" r="{gr}"/>', f'<ellipse cx="{gx}" cy="{gy}" rx="12" ry="{gr}"/>', '<path d="M100 2V138M30 114H170"/>'] + \
            [f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="96"/>' for c in cs2]
m.dims += [(136, 20, "globe  R 30"), (130, 134, "legs  arcs of R 96"), (20, 110, "crossbar  y 114")]
MARKS.append(m)

# 3 Orbit A: a pointed A with an elliptical orbit woven through its legs as the crossbar
m = Mark("Orbit A", "A pointed A of two circular arcs, with a tilted elliptical orbit woven through its legs: over the left leg, under the right. The orbit is the crossbar, and it turns the letter into a small world with something circling it.")
L3, R3, cs3 = gothic((100, 14), 38, 128, 130)
orb = ellipse_pts(100, 86, 74, 20, -10, 720)
m.interlace([L3 + L3[::-1][1:-1], R3 + R3[::-1][1:-1], orb], 6, lambda i, j, k: (i, j) == (0, 2), span=10)
m.strokes = [(d_of(L3, False), 6), (d_of(R3, False), 6), (d_of(orb), 6)]
m.guides += ['<ellipse cx="100" cy="86" rx="74" ry="20" transform="rotate(-10 100 86)"/>', '<path d="M100 2V138"/>'] + [f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="130"/>' for c in cs3]
m.dims += [(150, 120, "orbit  74 × 20 at −10°"), (128, 22, "legs  arcs of R 130")]
MARKS.append(m)

# 4 Armillary: a circle and two ellipses woven over and under around one centre
m = Mark("Armillary", "A circle and two tilted ellipses woven over and under one another, like the rings of an armillary sphere, the old instrument for modelling the heavens. Audi's rings link side by side; these link around one centre, so the mark reads as a globe.")
r0 = ellipse_pts(100, 70, 58, 58, 0, 720); r1 = ellipse_pts(100, 70, 58, 20, -28, 720); r2 = ellipse_pts(100, 70, 58, 20, 28, 720)
m.interlace([r0, r1, r2], 7, lambda i, j, k: k % 2 == 0)
m.guides += ['<circle cx="100" cy="70" r="58"/>', '<ellipse cx="100" cy="70" rx="58" ry="20" transform="rotate(-28 100 70)"/>',
             '<ellipse cx="100" cy="70" rx="58" ry="20" transform="rotate(28 100 70)"/>', '<path d="M100 2V138M30 70H170"/>']
m.dims += [(162, 22, "R  58"), (140, 132, "E  58 × 20 at ±28°")]
MARKS.append(m)

# 5 Borromean rings: three rings in a triangle, top and two feet like an A
m = Mark("Borromean", "Three rings in a triangle, linked so that no two are joined but all three hold together: cut any one and the others fall apart. The top ring and the two lower ones sit where an A's apex and feet would be. For Lab Atlas they stand for the wet lab, the computer and the field, which only work together.")
c = [(100, 46), (78, 84), (122, 84)]
rings = [ellipse_pts(x, y, 30, 30, 0, 720) for x, y in c]
m.interlace(rings, 6.5, lambda i, j, k: {(0, 1): True, (1, 2): True, (0, 2): False}[(i, j)])
m.guides += [f'<circle cx="{x}" cy="{y}" r="30"/>' for x, y in c] + ['<path d="M100 46L78 84L122 84Z"/>']
m.dims += [(140, 24, "R  30"), (50, 134, "centres on an equilateral triangle, side 44")]
MARKS.append(m)

# ---------------------------------------------------------------- renderers
def flat(mk, ink, uid, bg):
    out = "".join(f'<path d="{d}" fill="{ink}" fill-rule="evenodd"/>' for d in mk.fills)
    out += "".join(f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{w}" stroke-linejoin="round"/>' for d, w in mk.strokes)
    out += "".join(f'<path d="{d}" fill="none" stroke="{bg}" stroke-width="{w + 5}" stroke-linecap="butt"/><path d="{d}" fill="none" stroke="{ink}" stroke-width="{w}" stroke-linecap="butt"/>' for d, w in mk.overs)
    return out

def chrome(mk, uid, bg="#121316"):
    g = (f'<defs><linearGradient id="{uid}c" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{H}">'
         '<stop offset="0" stop-color="#ffffff"/><stop offset=".3" stop-color="#d6dae0"/><stop offset=".48" stop-color="#7b818b"/>'
         '<stop offset=".52" stop-color="#5d636c"/><stop offset=".7" stop-color="#e9ecef"/><stop offset="1" stop-color="#a3a9b1"/></linearGradient>'
         f'<linearGradient id="{uid}h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>')
    def layer(dx, dy, paint, extra_w=0, op=1):
        s = "".join(f'<path d="{d}" transform="translate({dx} {dy})" fill="{paint}" fill-rule="evenodd" opacity="{op}"/>' for d in mk.fills) if extra_w == 0 else \
            "".join(f'<path d="{d}" transform="translate({dx} {dy})" fill="{paint}" fill-rule="evenodd" stroke="{paint}" stroke-width="{extra_w}" opacity="{op}"/>' for d in mk.fills)
        s += "".join(f'<path d="{d}" transform="translate({dx} {dy})" fill="none" stroke="{paint}" stroke-width="{w + extra_w}" stroke-linejoin="round" opacity="{op}"/>' for d, w in mk.strokes)
        return s
    out = g + layer(0, 2.2, "#000", 1.6, .55) + layer(0, .9, "#1c1e22", 1.2) + layer(0, 0, f"url(#{uid}c)")
    out += "".join(f'<path d="{d}" fill="none" stroke="{bg}" stroke-width="{w + 5}"/><path d="{d}" transform="translate(0 .9)" fill="none" stroke="#1c1e22" stroke-width="{w + 1.2}"/><path d="{d}" fill="none" stroke="url(#{uid}c)" stroke-width="{w}"/>' for d, w in mk.overs)
    out += "".join(f'<path d="{d}" transform="translate(0 -.8)" fill="none" stroke="#fff" stroke-width="{w*.22:.2f}" opacity=".55" stroke-linejoin="round"/>' for d, w in mk.strokes)
    return out

def construction(mk, uid):
    gl = "".join(mk.guides)
    out = f'<g fill="none" stroke="var(--guide)" stroke-width=".55" stroke-dasharray="2 2">{gl}</g>'
    out += f'<g opacity=".9">{flat(mk, "var(--ink2)", uid, "var(--paper)")}</g>'
    out += "".join(f'<text x="{x}" y="{y}" font-size="5.4" fill="var(--guide)" font-family="ui-monospace,monospace">{html.escape(t)}</text>' for x, y, t in mk.dims)
    return out

def svg(body, w=None, cls=""):
    return f'<svg viewBox="0 0 {W} {H}" {f"width={w}" if w else ""} class="{cls}" aria-hidden="true">{body}</svg>'

def icon(mk, uid, size, bg, ink):
    return f'<svg viewBox="-6 -24 212 188" width="{size}" height="{size}" aria-hidden="true">{flat(mk, ink, uid, bg)}</svg>'

CSS = """
/* Layout: a marque book. Dark hero with the lead badge in chrome, then one spread per marque: flat, chrome, construction. */
:root{--bg:#f2f1ee;--fg:#121316;--fg2:#5c5f66;--rule:#dcdbd6;--paper:#fbfaf7;--guide:#8f8a80;--ink2:#121316;--sans:'Atlas Text',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0c0d0f;--fg:#ecebe7;--fg2:#9b9ea5;--rule:#26282c;--paper:#16171a;--guide:#7d7a73;--ink2:#ecebe7;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0c0d0f;--fg:#ecebe7;--fg2:#9b9ea5;--rule:#26282c;--paper:#16171a;--guide:#7d7a73;--ink2:#ecebe7;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:15px;line-height:1.55;margin:0}
.hero{background:radial-gradient(120% 90% at 50% 30%,#2a2c31 0%,#121316 60%,#0a0b0c 100%);color:#ecebe7;padding-block:56px 40px;padding-inline:clamp(16px,4vw,40px)}
.hero .in{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:32px;align-items:center}
.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#9b9ea5;margin:0 0 12px}
h1{font-weight:300;font-size:clamp(36px,5vw,64px);letter-spacing:-.02em;line-height:1;margin:0 0 16px;text-wrap:balance}
.hero p.lede{color:#b9bbc0;max-width:52ch;margin:0}
.hero svg{width:100%;height:auto;filter:drop-shadow(0 18px 30px rgba(0,0,0,.6))}
.wrap{max-width:1180px;margin:0 auto;padding-inline:clamp(16px,4vw,40px);padding-block:40px 72px}
.rules{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;padding-bottom:28px;border-bottom:1px solid var(--rule)}
.rules b{display:block;font-weight:500;margin-bottom:4px}
.rules p{margin:0;color:var(--fg2);font-size:13.5px}
.spread{display:grid;grid-template-columns:minmax(0,1fr);gap:14px;padding-block:36px;border-bottom:1px solid var(--rule)}
.head{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.head .no{font-variant-numeric:tabular-nums;color:var(--fg2);font-size:14px}
.head h2{font-weight:400;font-size:28px;letter-spacing:-.01em;margin:0}
.head .sizes{margin-left:auto;display:flex;gap:8px;align-items:center}
.idea{color:var(--fg2);max-width:72ch;margin:0}
.panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.panel{border-radius:6px;overflow:hidden;display:flex;flex-direction:column;min-width:0}
.panel .cap{font-size:11px;letter-spacing:.12em;text-transform:uppercase;padding:10px 12px;color:var(--fg2);background:var(--paper);border-top:1px solid var(--rule)}
.panel .art{aspect-ratio:10/7;max-width:100%;display:grid;place-items:center;padding:8%}
.panel .art svg{width:100%;height:auto}
.p-flat .art{background:#121316}
.p-chrome .art{background:radial-gradient(110% 100% at 50% 20%,#2c2e33,#121316 70%)}
.p-build .art{background:var(--paper)}
.chip{display:grid;place-items:center;border-radius:8px}
@media (max-width:820px){.hero .in{grid-template-columns:minmax(0,1fr)}.panels{grid-template-columns:minmax(0,1fr)}}
"""

def page(fonts, full_doc):
    lead = MARKS[0]
    spreads = ""
    for i, mk in enumerate(MARKS, 1):
        sizes = (f'<span class="chip" style="background:#121316;width:40px;height:40px">{icon(mk, f"i{i}a", 34, "#121316", "#fff")}</span>'
                 f'<span class="chip" style="background:#fff;width:40px;height:40px;box-shadow:inset 0 0 0 1px var(--rule)">{icon(mk, f"i{i}b", 34, "#fff", "#121316")}</span>'
                 f'<span class="chip" style="background:#121316;width:16px;height:16px;border-radius:4px">{icon(mk, f"i{i}c", 15, "#121316", "#fff")}</span>')
        spreads += f'''<section class="spread">
  <div class="head"><span class="no">{i:02d}</span><h2>{html.escape(mk.name)}</h2><span class="sizes" title="Icon sizes">{sizes}</span></div>
  <p class="idea">{html.escape(mk.idea)}</p>
  <div class="panels">
    <figure class="panel p-flat" style="margin:0"><div class="art">{svg(flat(mk, "#f4f3ef", f"f{i}", "#121316"))}</div><figcaption class="cap">Flat</figcaption></figure>
    <figure class="panel p-chrome" style="margin:0"><div class="art">{svg(chrome(mk, f"c{i}", "#1e2024"))}</div><figcaption class="cap">Chrome badge</figcaption></figure>
    <figure class="panel p-build" style="margin:0"><div class="art">{svg(construction(mk, f"g{i}"))}</div><figcaption class="cap">Construction</figcaption></figure>
  </div>
</section>'''
    body = f'''<header class="hero"><div class="in">
  <div><p class="eyebrow">Lab Atlas · round nine</p><h1>Marques from circles and ellipses</h1>
  <p class="lede">Five emblems built the way Audi's rings and Toyota's ellipses are: only circles and ellipses, at one consistent weight, symmetrical, with a reason behind every ring. Each one is shown flat, stamped in chrome, and as its construction drawing.</p></div>
  <div>{svg(chrome(lead, "hero", "#1a1b1f"))}</div>
</div></header>
<div class="wrap">
  <div class="rules">
    <div><b>Only primitives</b><p>Every line is an arc of a circle or an ellipse, with nothing freehand. That gives these marks the machined calm of a car badge.</p></div>
    <div><b>One weight</b><p>A single stroke weight per mark, or Toyota-style rings whose weight comes from offsetting two ellipses.</p></div>
    <div><b>Symmetry and linkage</b><p>Rings overlap, interlock or share a centre, like Audi's four and Toyota's three.</p></div>
    <div><b>A reason for each ring</b><p>Meridians, the equator, the titan's arch, an orbit, an armillary sphere, three linked kinds of lab. Each part stands for something.</p></div>
  </div>
  {spreads}
</div>'''
    head = f'<title>Lab Atlas Marques</title>\n<style>\n{fonts}\n{CSS}\n</style>'
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

def export():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for i, mk in enumerate(MARKS, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", mk.name.lower()).strip("-")
        for k, bg, ink in (("black", "#121316", "#f4f3ef"), ("white", "#ffffff", "#121316")):
            open(os.path.join(out, f"{i:02d}-{slug}-{k}.svg"), "w").write(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -10 220 160" width="660" height="480"><rect x="-10" y="-10" width="220" height="160" fill="{bg}"/>{flat(mk, ink, "x", bg)}</svg>\n')
        open(os.path.join(out, f"{i:02d}-{slug}-chrome.svg"), "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -10 220 160" width="660" height="480"><rect x="-10" y="-10" width="220" height="160" fill="#1e2024"/>{chrome(mk, "x", "#1e2024")}</svg>\n')

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "index.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built", len(MARKS))
