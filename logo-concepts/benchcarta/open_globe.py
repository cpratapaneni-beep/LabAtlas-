"""Open Globe, turned: the Benchcarta Open Globe rotated 90 degrees, with a science reference in each variant.

Usage: python3 open_globe.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bcb", os.path.join(HERE, "build.py"))
BC = importlib.util.module_from_spec(spec); sys_argv = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(BC); sys.argv = sys_argv
MQ = BC.MQ
Mark, ellipse_pts, d_of, flat, chrome, construction, svg, icon, arc = MQ.Mark, MQ.ellipse_pts, MQ.d_of, MQ.flat, MQ.chrome, MQ.construction, MQ.svg, MQ.icon, BC.arc

CX, CY, R, GAP = 100, 84, 50, 36          # globe centre, radius, half-angle of the opening
def ring_up(gap=GAP):  return arc(CX, CY, R, -90 + gap, 270 - gap)       # opening faces north
def ring_down(cy=56): return arc(CX, cy, R, 90 + GAP, 450 - GAP)  # opening faces south
def circle(cx, cy, r, n=90): return d_of(ellipse_pts(cx, cy, r, r, 0, n))
def neck_x(gap=GAP): return R*math.sin(math.radians(gap))                # half-width of the opening
def top_y(gap=GAP): return CY - R*math.cos(math.radians(gap))            # height where the opening sits

V = []

# 0 The original, for reference
m = Mark("Open Globe, as it was", "The mark you picked: a globe drawn as a C that opens east, with its equator running out through the opening to a point.")
m.strokes += [(arc(100, 70, 56, 36, 324), 7), (d_of(ellipse_pts(100, 70, 22, 56, 0, 240)), 4), ("M44 70H162", 4)]
m.fills += [circle(166, 70, 7)]
V.append(m)

# 1 Flask: opening north, short neck rising from the opening, globe lines inside the bulb
FG = 19
nx, ty = neck_x(FG), top_y(FG)
m = Mark("Flask Globe", "Turned so the opening faces up, the globe becomes a round-bottom flask. Two straight walls rise from the opening as its neck and end at a lip. Inside, the latitude and the axis still make it a globe. The axis runs on up out of the neck to a point, so the lab and the map stay one shape.")
m.strokes += [(ring_up(FG), 7), (f"M{CX - nx:.2f} {ty:.2f}V16M{CX + nx:.2f} {ty:.2f}V16", 7), (f"M{CX - nx - 7:.2f} 16H{CX + nx + 7:.2f}", 7),
              (d_of(ellipse_pts(CX, CY, R, 18, 0, 240)), 4), (f"M{CX} {CY + R}V30", 4)]
m.fills += [circle(CX, 30, 5.5)]
m.guides += [f'<circle cx="{CX}" cy="{CY}" r="{R}"/>', f'<ellipse cx="{CX}" cy="{CY}" rx="{R}" ry="18"/>', f'<path d="M{CX} 2V138M2 {CY}H198"/>',
             f'<path d="M{CX} {CY}L{CX - 70*math.sin(math.radians(FG)):.1f} {CY - 70*math.cos(math.radians(FG)):.1f}M{CX} {CY}L{CX + 70*math.sin(math.radians(FG)):.1f} {CY - 70*math.cos(math.radians(FG)):.1f}"/>']
m.dims += [(156, 40, "R  50, open ±19°"), (128, 12, "neck to y 16"), (8, 100, "latitude  50 × 18")]
V.append(m)

# 2 Rising bubbles: opening north, the axis rises out of the opening into a trail of bubbles
m = Mark("Rising Bubbles", "Turned upward, with the axis leaving the opening as a reaction does: a line rising into three bubbles that get bigger as they go. The globe reads as a flask on the bench, and the bubbles as something being discovered. The ellipse inside is the liquid's surface and the equator at once.")
m.strokes += [(ring_up(), 7), (d_of(ellipse_pts(CX, CY, R, 16, 0, 240)), 4), (f"M{CX} {CY + R}V{ty + 4:.1f}", 4)]
m.fills += [circle(CX, ty - 4, 3.5), circle(CX + 8, ty - 17, 5), circle(CX - 3, ty - 32, 6.5)]
m.guides += [f'<circle cx="{CX}" cy="{CY}" r="{R}"/>', f'<ellipse cx="{CX}" cy="{CY}" rx="{R}" ry="16"/>', f'<path d="M{CX} 2V138M2 {CY}H198"/>']
m.dims += [(156, 40, "R  50, open ±36°"), (122, 14, "bubbles  r 3.5 · 5 · 6.5")]
V.append(m)

# 3 Molecule: opening north, the axis rises to a hexagonal ring, the symbol of organic chemistry
hx, hy, hr = CX, 22, 12
hexd = "M" + "L".join(f"{hx + hr*math.cos(math.radians(-90 + 60*i)):.2f} {hy + hr*math.sin(math.radians(-90 + 60*i)):.2f}" for i in range(6)) + "Z"
m = Mark("Molecule", "Turned upward, the axis rises out of the opening and ends in a hexagon, the benzene ring every chemistry student learns to draw. The point at the end of the line, where the map leads, becomes a molecule.")
m.strokes += [(ring_up(), 7), (d_of(ellipse_pts(CX, CY, R, 18, 0, 240)), 4), (f"M{CX} {CY + R}V{hy + hr:.1f}", 4), (hexd, 4.5)]
m.guides += [f'<circle cx="{CX}" cy="{CY}" r="{R}"/>', f'<circle cx="{hx}" cy="{hy}" r="{hr}"/>', f'<path d="M{CX} 2V138M2 {CY}H198"/>']
m.dims += [(156, 40, "R  50, open ±36°"), (118, 16, "hexagon  R 12")]
V.append(m)

# 4 Atom: opening north, two electron orbits cross inside the globe around a nucleus
m = Mark("Atom Globe", "Turned upward, with the globe's lines replaced by two crossing electron orbits around a nucleus, Rutherford's atom inside the map. The axis still leaves through the opening to a point.")
m.strokes += [(ring_up(), 7), (d_of(ellipse_pts(CX, CY, R - 4, 15, 30, 240)), 4), (d_of(ellipse_pts(CX, CY, R - 4, 15, -30, 240)), 4), (f"M{CX} {CY - 10}V30", 4)]
m.fills += [circle(CX, CY, 7), circle(CX, 30, 5.5)]
m.guides += [f'<circle cx="{CX}" cy="{CY}" r="{R}"/>', f'<ellipse cx="{CX}" cy="{CY}" rx="{R - 4}" ry="15" transform="rotate(30 {CX} {CY})"/>',
             f'<ellipse cx="{CX}" cy="{CY}" rx="{R - 4}" ry="15" transform="rotate(-30 {CX} {CY})"/>', f'<path d="M{CX} 2V138M2 {CY}H198"/>']
m.dims += [(156, 40, "R  50, open ±36°"), (140, 132, "orbits  46 × 15 at ±30°")]
V.append(m)

CSS = BC.CSS + """
.compare{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0 0}
.compare figure{margin:0;background:#121316;border-radius:6px;padding:10px 10px 8px;display:flex;flex-direction:column;gap:6px;align-items:center}
.compare figcaption{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#9b9ea5}
.compare svg{width:100%;height:auto}
"""

def page(fonts, full_doc):
    lead = V[1]
    strip = "".join(f'<figure><svg viewBox="-10 -10 220 160" aria-hidden="true">{flat(mk, "#f4f3ef", f"s{i}", "#121316").replace("@@", f"s{i}-")}</svg><figcaption>{html.escape(mk.name)}</figcaption></figure>' for i, mk in enumerate(V))
    spreads = ""
    for i, mk in enumerate(V[1:], 1):
        sizes = (f'<span class="chip" style="background:#121316;width:40px;height:40px">{icon(mk, f"i{i}a", 34, "#121316", "#fff")}</span>'
                 f'<span class="chip" style="background:#fff;width:40px;height:40px;box-shadow:inset 0 0 0 1px var(--rule)">{icon(mk, f"i{i}b", 34, "#fff", "#121316")}</span>'
                 f'<span class="chip" style="background:#121316;width:16px;height:16px;border-radius:4px">{icon(mk, f"i{i}c", 15, "#121316", "#fff")}</span>')
        locks = (f'<div class="locks"><div class="lock" style="background:#121316;color:#f4f3ef">{icon(mk, f"l{i}a", 38, "#121316", "#f4f3ef")}<b>Benchcarta</b></div>'
                 f'<div class="lock" style="background:#fbfaf7;color:#121316;box-shadow:inset 0 0 0 1px var(--rule)">{icon(mk, f"l{i}b", 38, "#fbfaf7", "#121316")}<b>Benchcarta</b></div></div>')
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
  <div><p class="eyebrow">Benchcarta · round two</p><h1>Open Globe, turned</h1>
  <p class="lede">The Open Globe turned 90 degrees to the left, so the opening and its point face the top. With the opening facing up, the globe becomes a round-bottom flask, so the science is in the shape itself. Each version below adds a second reference at the point where the line leaves the globe: a flask neck, rising bubbles, a molecule, or an atom.</p></div>
  <div>{svg(chrome(lead, "hero", "#1a1b1f"))}</div>
</div></header>
<div class="wrap">
  <div class="compare">{strip}</div>
  {spreads}
</div>'''
    head = f'<title>Benchcarta Open Globe</title>\n<style>\n{fonts}\n{CSS}\n</style>'
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

def export():
    out = os.path.join(HERE, "svg-open-globe"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for i, mk in enumerate(V[1:], 1):
        slug = re.sub(r"[^a-z0-9]+", "-", mk.name.lower()).strip("-")
        for k, bg, ink in (("black", "#121316", "#f4f3ef"), ("white", "#ffffff", "#121316")):
            open(os.path.join(out, f"{i:02d}-{slug}-{k}.svg"), "w").write(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -10 220 160" width="660" height="480"><rect x="-10" y="-10" width="220" height="160" fill="{bg}"/>{flat(mk, ink, "x", bg)}</svg>\n')
        open(os.path.join(out, f"{i:02d}-{slug}-chrome.svg"), "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -10 220 160" width="660" height="480"><rect x="-10" y="-10" width="220" height="160" fill="#1e2024"/>{chrome(mk, "x", "#1e2024")}</svg>\n')

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "open-globe.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built", len(V) - 1)
