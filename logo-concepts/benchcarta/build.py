"""Benchcarta marks: bench + carta (map). Emblems built only from circles, ellipses and straight
lines, in the tradition of automotive badges, each shown flat, in chrome, and as a construction drawing.

Usage: python3 build.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("marques", os.path.join(HERE, "..", "emblem-marques", "build.py"))
MQ = importlib.util.module_from_spec(spec); spec.loader.exec_module(MQ)
Mark, ellipse_pts, d_of, flat, chrome, construction, svg, icon, W, H = MQ.Mark, MQ.ellipse_pts, MQ.d_of, MQ.flat, MQ.chrome, MQ.construction, MQ.svg, MQ.icon, MQ.W, MQ.H

def arc(cx, cy, r, a0, a1):
    """SVG arc path on a circle from angle a0 to a1 (degrees, clockwise in screen space)."""
    p0 = (cx + r*math.cos(math.radians(a0)), cy + r*math.sin(math.radians(a0)))
    p1 = (cx + r*math.cos(math.radians(a1)), cy + r*math.sin(math.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{p0[0]:.2f} {p0[1]:.2f}A{r} {r} 0 {large} 1 {p1[0]:.2f} {p1[1]:.2f}"

MARKS = []

# 1 Two hemispheres: the B's bowls are the twin hemispheres of an old world map
m = Mark("Hemisphere B", "The B's two bowls are the two hemispheres of an old world map, stacked on a straight stem. The upper globe is smaller and sits tangent on the lower one, as a B's bowls do. Each has one meridian and one parallel. It's the clearest link between the letter and the map in the name.")
ux, uy, ur = 92, 37, 25
lx, ly, lr = 102, 99, 35
stem_x = 67
m.strokes += [(f"M{stem_x} 12V134", 7), (arc(ux, uy, ur, -180 + 0.01, 180), 7), (arc(lx, ly, lr, -180 + 0.01, 180), 7)]
m.strokes = [(f"M{stem_x} 12V134", 7), (d_of(ellipse_pts(ux, uy, ur, ur, 0, 240)), 7), (d_of(ellipse_pts(lx, ly, lr, lr, 0, 240)), 7),
             (d_of(ellipse_pts(ux, uy, 10, ur, 0, 180)), 3.2), (f"M{ux - ur} {uy}A{ur} 6 0 0 0 {ux + ur} {uy}", 3.2),
             (d_of(ellipse_pts(lx, ly, 14, lr, 0, 180)), 3.2), (f"M{lx - lr} {ly}A{lr} 8 0 0 0 {lx + lr} {ly}", 3.2)]
m.guides += [f'<circle cx="{ux}" cy="{uy}" r="{ur}"/>', f'<circle cx="{lx}" cy="{ly}" r="{lr}"/>', f'<path d="M{stem_x} 2V138M2 62H198"/>']
m.dims += [(124, 20, "upper  R 25"), (142, 132, "lower  R 35"), (8, 58, "bowls tangent at y 62")]
MARKS.append(m)

# 2 Linked b and c: two rings chained like Audi's, the left one a b, the right one an open c
m = Mark("Linked bc", "A lowercase b and c drawn as two equal rings and chained together like Audi's: the c passes over the b at the top and under it at the bottom. The bench and the map, linked. The c's opening faces east.")
bx, cx2, cy2, r = 78, 122, 80, 34
m.strokes += [(f"M{bx - r} 12V{cy2}", 8), (d_of(ellipse_pts(bx, cy2, r, r, 0, 360)), 8), (arc(cx2, cy2, r, 42, 318), 8)]
yi = math.sqrt(r*r - ((cx2 - bx)/2)**2)
a_top = math.degrees(math.atan2(-yi, -(cx2 - bx)/2))       # on the c, at the upper crossing
a_bot = math.degrees(math.atan2(yi, (cx2 - bx)/2))          # on the b, at the lower crossing
m.overs += [(arc(cx2, cy2, r, a_top - 12, a_top + 12), 8), (arc(bx, cy2, r, a_bot - 12, a_bot + 12), 8)]
m.guides += [f'<circle cx="{bx}" cy="{cy2}" r="{r}"/>', f'<circle cx="{cx2}" cy="{cy2}" r="{r}"/>', f'<path d="M{bx - r} 2V138M2 {cy2}H198M100 2V138"/>']
m.dims += [(140, 30, "R  34, centres 44 apart"), (150, 134, "c open ±42°")]
MARKS.append(m)

# 3 Bench globe: the world resting on a lab bench
m = Mark("Bench Globe", "A globe resting on a lab bench, which is the name in one picture: the bench, and the map of the world it opens onto. The bench is a straight top on two legs, and the globe touches it at a single point.")
gx, gy, gr = 100, 56, 34
m.strokes += [(d_of(ellipse_pts(gx, gy, gr, gr, 0, 360)), 7), (d_of(ellipse_pts(gx, gy, 13, gr, 0, 240)), 3.4),
              (f"M{gx - gr} {gy}A{gr} 9 0 0 0 {gx + gr} {gy}", 3.4), ("M22 98H178", 8), ("M42 98V130M158 98V130", 8)]
m.guides += [f'<circle cx="{gx}" cy="{gy}" r="{gr}"/>', '<path d="M100 2V138M2 98H198"/>', f'<circle cx="{gx}" cy="{gy + gr}" r="2.5"/>']
m.dims += [(140, 24, "globe  R 34"), (8, 92, "bench top  y 98"), (120, 134, "legs  x 42, 158")]
MARKS.append(m)

# 4 Compass C: an open ring with a north-south compass needle standing inside it
m = Mark("Compass C", "An open C with a compass needle standing inside it, pointing north. The north half is solid and the south half is an outline, as on a mariner's compass. The C opens to the east.")
R = 54
m.strokes += [(arc(100, 70, R, 38, 322), 8), ("M90 70L100 122L110 70", 4)]
m.fills += ["M90 70L100 18L110 70Z", d_of(ellipse_pts(100, 70, 5.5, 5.5, 0, 60))]
m.guides += [f'<circle cx="100" cy="70" r="{R}"/>', '<path d="M100 2V138M2 70H198"/>', '<path d="M100 70L190 13M100 70L190 127"/>']
m.dims += [(146, 18, "R  54, open ±38°"), (112, 134, "needle  104 long")]
MARKS.append(m)

# 5 Contour C: three nested open rings, like the contour lines of a map
m = Mark("Contour C", "Three nested C's read as the contour lines of a survey map around a single summit, the point of the C. It's the simplest map symbol there is, made into the initial.")
m.strokes += [(arc(100, 70, 58, 40, 320), 7.5), (arc(100, 70, 40, 40, 320), 7.5), (arc(100, 70, 22, 40, 320), 7.5)]
m.fills += [d_of(ellipse_pts(100, 70, 6.5, 6.5, 0, 60))]
m.guides += ['<circle cx="100" cy="70" r="58"/>', '<circle cx="100" cy="70" r="40"/>', '<circle cx="100" cy="70" r="22"/>', '<path d="M100 70L190 -5.5M100 70L190 145.5M2 70H198"/>']
m.dims += [(150, 14, "R 58 · 40 · 22"), (150, 130, "open ±40°")]
MARKS.append(m)

# 6 Pin C: a map pin whose head holds an open C
m = Mark("Pin C", "A map pin with an open C inside its head: the place on the map where your bench is. It's the most literal mark, and the one that's easiest to understand at a glance.")
m.strokes += [("M100 134C84 112 58 92 58 58A42 42 0 0 1 142 58C142 92 116 112 100 134Z", 7), (arc(100, 58, 19, 45, 315), 7)]
m.guides += ['<circle cx="100" cy="58" r="42"/>', '<circle cx="100" cy="58" r="19"/>', '<path d="M100 2V138M2 58H198"/>']
m.dims += [(146, 20, "head  R 42"), (128, 130, "C  R 19, open ±45°")]
MARKS.append(m)

# 7 Open globe: a C-shaped globe whose equator runs out through the opening to a point
m = Mark("Open Globe", "A globe drawn as a C, open on the east side. Its equator runs straight out through the opening and ends in a single point, like a route leaving the map toward a place not yet charted.")
R = 56
m.strokes += [(arc(100, 70, R, 36, 324), 7), (arc(100, 70, R, 36, 324), 0)]
m.strokes += [(d_of(ellipse_pts(100, 70, 22, R, 0, 240)), 4), ("M44 70H162", 4)]
m.fills += [d_of(ellipse_pts(166, 70, 7, 7, 0, 60))]
m.guides += [f'<circle cx="100" cy="70" r="{R}"/>', f'<ellipse cx="100" cy="70" rx="22" ry="{R}"/>', '<path d="M100 2V138M2 70H198"/>']
m.dims += [(150, 16, "R  56, open ±36°"), (140, 92, "equator to x 166")]
MARKS.append(m)

CSS = MQ.CSS + """
.lock{display:flex;align-items:center;gap:12px;padding:16px 18px;border-radius:6px}
.lock b{font-weight:400;font-size:22px;letter-spacing:-.01em}
.locks{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:14px}
"""

def page(fonts, full_doc):
    lead = MARKS[0]
    spreads = ""
    for i, mk in enumerate(MARKS, 1):
        sizes = (f'<span class="chip" style="background:#121316;width:40px;height:40px">{icon(mk, f"i{i}a", 34, "#121316", "#fff")}</span>'
                 f'<span class="chip" style="background:#fff;width:40px;height:40px;box-shadow:inset 0 0 0 1px var(--rule)">{icon(mk, f"i{i}b", 34, "#fff", "#121316")}</span>'
                 f'<span class="chip" style="background:#121316;width:16px;height:16px;border-radius:4px">{icon(mk, f"i{i}c", 15, "#121316", "#fff")}</span>')
        locks = (f'<div class="locks"><div class="lock" style="background:#121316;color:#f4f3ef">{icon(mk, f"l{i}a", 34, "#121316", "#f4f3ef")}<b>Benchcarta</b></div>'
                 f'<div class="lock" style="background:#fbfaf7;color:#121316;box-shadow:inset 0 0 0 1px var(--rule)">{icon(mk, f"l{i}b", 34, "#fbfaf7", "#121316")}<b>Benchcarta</b></div></div>')
        spreads += f'''<section class="spread">
  <div class="head"><span class="no">{i:02d}</span><h2>{html.escape(mk.name)}</h2><span class="sizes" title="Icon sizes">{sizes}</span></div>
  <p class="idea">{html.escape(mk.idea)}</p>
  <div class="panels">
    <figure class="panel p-flat" style="margin:0"><div class="art">{svg(flat(mk, "#f4f3ef", f"f{i}", "#121316"))}</div><figcaption class="cap">Flat</figcaption></figure>
    <figure class="panel p-chrome" style="margin:0"><div class="art">{svg(chrome(mk, f"c{i}", "#1e2024"))}</div><figcaption class="cap">Chrome badge</figcaption></figure>
    <figure class="panel p-build" style="margin:0"><div class="art">{svg(construction(mk, f"g{i}"))}</div><figcaption class="cap">Construction</figcaption></figure>
  </div>
  {locks}
</section>'''
    body = f'''<header class="hero"><div class="in">
  <div><p class="eyebrow">Benchcarta · identity, round one</p><h1>Benchcarta</h1>
  <p class="lede">Bench, where the research happens, and carta, the Latin and Italian word for map: a map of the bench. These seven marks are built the way car badges are, only circles, ellipses and straight lines at one weight. Each is shown flat, stamped in chrome, as its construction drawing, and next to the name.</p></div>
  <div>{svg(chrome(lead, "hero", "#1a1b1f"))}</div>
</div></header>
<div class="wrap">
  <div class="rules">
    <div><b>Only primitives</b><p>Every line is part of a circle, an ellipse or a straight rule, and nothing is freehand.</p></div>
    <div><b>One weight</b><p>Each mark holds a single main stroke weight, with a lighter one only for globe lines.</p></div>
    <div><b>B, C, bench, map</b><p>Every mark is built from the name: the B, the C, the bench, the map, or two of them at once.</p></div>
    <div><b>Badge-ready</b><p>Each one works flat, embossed or stamped in metal, and at 16 pixels.</p></div>
  </div>
  {spreads}
</div>'''
    head = f'<title>Benchcarta Marks</title>\n<style>\n{fonts}\n{CSS}\n</style>'
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
