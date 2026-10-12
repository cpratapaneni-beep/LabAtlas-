"""Benchcarta, Atom Globe: a closed circle holding two electron orbits around a nucleus, with one
map reference added that leaves the circle unbroken. Four options for that reference.

Usage: python3 atom.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bcb", os.path.join(HERE, "build.py"))
BC = importlib.util.module_from_spec(spec); argv = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(BC); sys.argv = argv
MQ = BC.MQ
Mark, ellipse_pts, d_of, flat, chrome, construction, svg, icon = MQ.Mark, MQ.ellipse_pts, MQ.d_of, MQ.flat, MQ.chrome, MQ.construction, MQ.svg, MQ.icon

CX, CY, R = 100, 74, 50
ORX, ORY, TILT = 45, 15, 30

def base(m, nucleus=True):
    m.strokes += [(d_of(ellipse_pts(CX, CY, R, R, 0, 360)), 7),
                  (d_of(ellipse_pts(CX, CY, ORX, ORY, TILT, 360)), 4.2),
                  (d_of(ellipse_pts(CX, CY, ORX, ORY, -TILT, 360)), 4.2)]
    if nucleus: m.fills += [d_of(ellipse_pts(CX, CY, 7, 7, 0, 90))]
    m.guides += [f'<circle cx="{CX}" cy="{CY}" r="{R}"/>', f'<ellipse cx="{CX}" cy="{CY}" rx="{ORX}" ry="{ORY}" transform="rotate({TILT} {CX} {CY})"/>',
                 f'<ellipse cx="{CX}" cy="{CY}" rx="{ORX}" ry="{ORY}" transform="rotate({-TILT} {CX} {CY})"/>', f'<path d="M{CX} 2V138M2 {CY}H198"/>']
    m.dims += [(150, 132, "globe R 50 · orbits 45 × 15 at ±30°")]
    return m

V = []

# 1 North pointer: a compass north arrow above the globe, clear of the circle
m = base(Mark("North Pointer", "A small compass north arrow floats just above the globe, clear of the circle. It's the plainest map sign there is, and it says which way is up on any chart. The arrowhead is solid with a notched base, like the north mark on a compass card."))
m.fills += ["M100 1L109 19L100 14.5L91 19Z"]
m.guides += ['<path d="M100 1L109 19L91 19Z"/>']
m.dims += [(114, 12, "arrowhead 18 wide, 5 clear of the rim")]
V.append(m)

# 2 Compass ticks: cardinal marks outside the ring, north longest
m = base(Mark("Compass Ticks", "Four short marks stand outside the ring at north, east, south and west, with north the longest, so the globe sits in a compass. The circle stays whole; the marks start just beyond it."))
for a, L in ((-90, 16), (0, 9), (90, 9), (180, 9)):
    r0 = R + 7
    x0, y0 = CX + r0*math.cos(math.radians(a)), CY + r0*math.sin(math.radians(a))
    x1, y1 = CX + (r0 + L)*math.cos(math.radians(a)), CY + (r0 + L)*math.sin(math.radians(a))
    m.strokes += [(f"M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}", 5 if a == -90 else 4)]
m.guides += [f'<circle cx="{CX}" cy="{CY}" r="{R + 7}"/>']
m.dims += [(124, 12, "north 16 · others 9, from R 57")]
V.append(m)

# 3 Pin nucleus: the nucleus is a map pin, 'you are here' at the centre of the atom
pin_r = 7.5
tip = (CX, CY + 15)
t1 = (CX - pin_r*math.cos(math.radians(30)), CY - 2 + pin_r*math.sin(math.radians(30)))
t2 = (CX + pin_r*math.cos(math.radians(30)), t1[1])
pin = f"M{tip[0]} {tip[1]}L{t1[0]:.2f} {t1[1]:.2f}A{pin_r} {pin_r} 0 1 1 {t2[0]:.2f} {t2[1]:.2f}Z"
m = base(Mark("Pin Nucleus", "The nucleus becomes a map pin: 'you are here' at the centre of the atom. The orbits circle the place you're looking for. Nothing sits outside the circle, so the silhouette stays a perfect round."), nucleus=False)
m.fills += [pin]
m.overs_hole = (CX, CY - 2, 2.8)
m.guides += [f'<circle cx="{CX}" cy="{CY - 2}" r="{pin_r}"/>']
m.dims += [(118, 104, "pin  R 7.5, tip 60°")]
V.append(m)

# 4 Bezel: a fine graduated ring around the globe, like a compass dial
m = base(Mark("Compass Bezel", "A fine graduated ring around the globe, with a tick every 15°, a longer one every 90°, and a small solid pointer at north, like the dial of a compass. It's the richest of the four, best at large sizes and in metal."))
d = ""
for i in range(24):
    a = -90 + i*15
    L = 6 if i % 6 == 0 else 3
    r0 = R + 8
    if i == 0: continue
    x0, y0 = CX + r0*math.cos(math.radians(a)), CY + r0*math.sin(math.radians(a))
    x1, y1 = CX + (r0 + L)*math.cos(math.radians(a)), CY + (r0 + L)*math.sin(math.radians(a))
    d += f"M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}"
m.strokes += [(d, 2.2)]
m.fills += [f"M{CX} {CY - R - 8}L{CX - 5} {CY - R - 17}H{CX + 5}Z"]
m.guides += [f'<circle cx="{CX}" cy="{CY}" r="{R + 8}"/>', f'<circle cx="{CX}" cy="{CY}" r="{R + 14}"/>']
m.dims += [(132, 12, "ticks every 15°, from R 58")]
V.append(m)

def flat2(mk, ink, uid, bg):
    out = flat(mk, ink, uid, bg)
    if getattr(mk, "overs_hole", None):
        x, y, r = mk.overs_hole
        out += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{bg}"/>'
    return out

def chrome2(mk, uid, bg):
    out = chrome(mk, uid, bg)
    if getattr(mk, "overs_hole", None):
        x, y, r = mk.overs_hole
        out += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{bg}"/>'
    return out

def ico(mk, k, size, bg, ink):
    body = flat2(mk, ink, k, bg)
    return f'<svg viewBox="30 0 140 140" width="{size}" height="{size}" aria-hidden="true">{body}</svg>'

CSS = BC.CSS + """
.compare{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:0 0 8px}
.compare figure{margin:0;background:#121316;border-radius:6px;padding:14px 14px 10px;display:flex;flex-direction:column;gap:8px;align-items:center}
.compare figcaption{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#9b9ea5}
.compare svg{width:100%;height:auto}
"""

def page(fonts, full_doc):
    lead = V[0]
    strip = "".join(f'<figure><svg viewBox="30 0 140 140" aria-hidden="true">{flat2(mk, "#f4f3ef", f"s{i}", "#121316")}</svg><figcaption>{i+1:02d} · {html.escape(mk.name)}</figcaption></figure>' for i, mk in enumerate(V))
    spreads = ""
    for i, mk in enumerate(V, 1):
        sizes = (f'<span class="chip" style="background:#121316;width:40px;height:40px">{ico(mk, f"i{i}a", 34, "#121316", "#fff")}</span>'
                 f'<span class="chip" style="background:#fff;width:40px;height:40px;box-shadow:inset 0 0 0 1px var(--rule)">{ico(mk, f"i{i}b", 34, "#fff", "#121316")}</span>'
                 f'<span class="chip" style="background:#121316;width:16px;height:16px;border-radius:4px">{ico(mk, f"i{i}c", 15, "#121316", "#fff")}</span>')
        locks = (f'<div class="locks"><div class="lock" style="background:#121316;color:#f4f3ef">{ico(mk, f"l{i}a", 40, "#121316", "#f4f3ef")}<b>Benchcarta</b></div>'
                 f'<div class="lock" style="background:#fbfaf7;color:#121316;box-shadow:inset 0 0 0 1px var(--rule)">{ico(mk, f"l{i}b", 40, "#fbfaf7", "#121316")}<b>Benchcarta</b></div></div>')
        spreads += f'''<section class="spread">
  <div class="head"><span class="no">{i:02d}</span><h2>{html.escape(mk.name)}</h2><span class="sizes" title="Icon sizes">{sizes}</span></div>
  <p class="idea">{html.escape(mk.idea)}</p>
  <div class="panels">
    <figure class="panel p-flat" style="margin:0"><div class="art">{svg(flat2(mk, "#f4f3ef", f"f{i}", "#121316"))}</div><figcaption class="cap">Flat</figcaption></figure>
    <figure class="panel p-chrome" style="margin:0"><div class="art">{svg(chrome2(mk, f"c{i}", "#1e2024"))}</div><figcaption class="cap">Chrome badge</figcaption></figure>
    <figure class="panel p-build" style="margin:0"><div class="art">{svg(construction(mk, f"g{i}"))}</div><figcaption class="cap">Construction</figcaption></figure>
  </div>
  {locks}
</section>'''
    body = f'''<header class="hero"><div class="in">
  <div><p class="eyebrow">Benchcarta · round three</p><h1>Atom Globe</h1>
  <p class="lede">The circle is closed and the line is gone. What's left is a whole globe holding two electron orbits around a nucleus. Each version adds one map reference that leaves the circle unbroken: a north pointer, compass ticks, a map-pin nucleus, or a compass bezel.</p></div>
  <div>{svg(chrome2(lead, "hero", "#1a1b1f"))}</div>
</div></header>
<div class="wrap">
  <div class="compare">{strip}</div>
  {spreads}
</div>'''
    head = f'<title>Benchcarta Atom Globe</title>\n<style>\n{fonts}\n{CSS}\n</style>'
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

def export():
    out = os.path.join(HERE, "svg-atom"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for i, mk in enumerate(V, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", mk.name.lower()).strip("-")
        for k, bg, ink in (("black", "#121316", "#f4f3ef"), ("white", "#ffffff", "#121316")):
            open(os.path.join(out, f"{i:02d}-{slug}-{k}.svg"), "w").write(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 0 140 140" width="512" height="512"><rect x="30" y="0" width="140" height="140" fill="{bg}"/>{flat2(mk, ink, "x", bg)}</svg>\n')
        open(os.path.join(out, f"{i:02d}-{slug}-chrome.svg"), "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 0 140 140" width="512" height="512"><rect x="30" y="0" width="140" height="140" fill="#1e2024"/>{chrome2(mk, "x", "#1e2024")}</svg>\n')

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "atom.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built", len(V))
