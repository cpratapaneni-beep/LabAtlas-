"""Benchcarta mark: Compass Bezel atom globe with three orbits 60 degrees apart.

Usage: python3 final.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("atom", os.path.join(HERE, "atom.py"))
AT = importlib.util.module_from_spec(spec); argv = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(AT); sys.argv = argv
MQ = AT.MQ
Mark, ellipse_pts, d_of, construction, svg = MQ.Mark, MQ.ellipse_pts, MQ.d_of, MQ.construction, MQ.svg
flat2, chrome2, ico = AT.flat2, AT.chrome2, AT.ico
CX, CY, R, ORX, ORY = AT.CX, AT.CY, AT.R, AT.ORX, AT.ORY

# Electrons: one per orbit, at each orbit's outer end, so they sit 120 degrees apart around the nucleus.
ELECTRON_T = 40
ELECTRONS = [(270, "#a98ad4", "#c9a2f2"), (150, "#cf5f49", "#e0705a"), (30, "#3b8ccc", "#5fa8de")]   # (angle, base, highlight)
def electrons(mk, bg, r=5.2, gap=2.2, chrome=False, uid="e"):
    if not getattr(mk, "electron_r", None): return ""
    r = mk.electron_r; out = ""
    light = bg in ("#fbfaf7", "#ffffff", "#fff", "#f4f3ef", "var(--paper)")
    # nucleus: the three dots of the original Lab Atlas logo, coral, purple and blue on a thin line
    sp, nr, lw = mk.nucleus
    line_c = "#121316" if light else "#f4f3ef"
    out += f'<path d="M{CX - sp} {CY}H{CX + sp}" stroke="{line_c}" stroke-width="{lw}" opacity=".55"/>'
    for j, (dx, (_, c, hi)) in enumerate(zip((-sp, 0, sp), (ELECTRONS[1], ELECTRONS[0], ELECTRONS[2]))):
        if chrome:
            gid = f"{uid}n{j}"
            out += (f'<defs><radialGradient id="{gid}" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
                    f'<stop offset=".25" stop-color="{hi}"/><stop offset="1" stop-color="{c}"/></radialGradient></defs>'
                    f'<circle cx="{CX + dx}" cy="{CY + .7}" r="{nr}" fill="#000" opacity=".45"/><circle cx="{CX + dx}" cy="{CY}" r="{nr}" fill="url(#{gid})"/>')
        else:
            out += f'<circle cx="{CX + dx}" cy="{CY}" r="{nr}" fill="{c if light else hi}"/>'
    for i, (a, c, hi) in enumerate(ELECTRONS):
        t = math.radians(ELECTRON_T)                       # same position along every orbit keeps the 120-degree rotational symmetry
        lx, ly = ORX*math.cos(t), ORY*math.sin(t); ph = math.radians(a)
        x, y = CX + lx*math.cos(ph) - ly*math.sin(ph), CY + lx*math.sin(ph) + ly*math.cos(ph)
        out += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r + gap}" fill="{bg}"/>'
        if chrome:
            gid = f"{uid}g{i}"
            out += (f'<defs><radialGradient id="{gid}" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
                    f'<stop offset=".25" stop-color="{hi}"/><stop offset="1" stop-color="{c}"/></radialGradient></defs>'
                    f'<circle cx="{x:.2f}" cy="{y + .9:.2f}" r="{r}" fill="#000" opacity=".45"/><circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="url(#{gid})"/>')
        else:
            out += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{c if light else hi}"/>'
    return out

_flat2, _chrome2, _construction = flat2, chrome2, construction
def flat2(mk, ink, uid, bg): return _flat2(mk, ink, uid, bg) + electrons(mk, bg)
def chrome2(mk, uid, bg): return _chrome2(mk, uid, bg) + electrons(mk, bg, chrome=True, uid=uid)
def construction(mk, uid): return _construction(mk, uid) + electrons(mk, "var(--paper)")
def ico(mk, k, size, bg, ink):
    return f'<svg viewBox="30 0 140 140" width="{size}" height="{size}" aria-hidden="true">{flat2(mk, ink, k, bg)}</svg>'

m = Mark("Benchcarta", "A globe holding three electron orbits set 60° apart around a nucleus, inside a compass bezel. Three electrons, in coral, purple and blue, ride the orbits at matching points, 120° apart, and the nucleus is the three dots of the original Lab Atlas logo. The three orbits make the atom fully symmetrical; the bezel's ticks every 15° and its north pointer make the globe a compass.")
m.strokes += [(d_of(ellipse_pts(CX, CY, R, R, 0, 360)), 7)] + [(d_of(ellipse_pts(CX, CY, ORX, ORY, t, 360)), 2.8) for t in (30, -30, 90)]
m.electron_r = 5.2
m.nucleus = (9.5, 3.6, 1.8)        # dot spacing, dot radius, line weight
d = ""
for i in range(1, 24):
    a = -90 + i*15; L = 6 if i % 6 == 0 else 3; r0 = R + 8
    d += f"M{CX + r0*math.cos(math.radians(a)):.2f} {CY + r0*math.sin(math.radians(a)):.2f}L{CX + (r0 + L)*math.cos(math.radians(a)):.2f} {CY + (r0 + L)*math.sin(math.radians(a)):.2f}"
m.strokes += [(d, 2.2)]
m.fills += [f"M{CX} {CY - R - 8}L{CX - 5} {CY - R - 17}H{CX + 5}Z"]
m.guides += [f'<circle cx="{CX}" cy="{CY}" r="{R}"/>', f'<circle cx="{CX}" cy="{CY}" r="{R + 8}"/>', f'<circle cx="{CX}" cy="{CY}" r="{R + 14}"/>'] + \
            [f'<ellipse cx="{CX}" cy="{CY}" rx="{ORX}" ry="{ORY}" transform="rotate({t} {CX} {CY})"/>' for t in (30, -30, 90)] + \
            [f'<path d="M{CX} 2V138M2 {CY}H198"/>'] + [f'<path d="M{CX} {CY}L{CX + 66*math.cos(math.radians(t)):.1f} {CY + 66*math.sin(math.radians(t)):.1f}"/>' for t in (30, 150, 90)]
m.dims += [(124, 10, "ticks every 15°"), (110, 136, "orbits 60° apart"), (4, 68, "globe R 50")]

small = Mark("Benchcarta small", "")
small.strokes += [(d_of(ellipse_pts(CX, CY, R, R, 0, 360)), 9)] + [(d_of(ellipse_pts(CX, CY, ORX, ORY, t, 360)), 4.4) for t in (30, -30, 90)]
small.electron_r = 7
small.nucleus = (8.6, 3.7, 2.4)
def ico_s(k, size, bg, ink):
    return f'<svg viewBox="44 18 112 112" width="{size}" height="{size}" aria-hidden="true">{flat2(small, ink, k, bg)}</svg>'

CSS = AT.CSS + """
.apps{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-end;margin-top:14px}
.apps figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:8px;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--fg2)}
.app{display:grid;place-items:center}
.spec{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;align-content:start}
.spec div{border-top:1px solid var(--rule);padding-top:10px}
.spec b{display:block;font-weight:500;margin-bottom:2px}
.spec span{color:var(--fg2);font-size:13.5px}
h3.sec{font-weight:400;font-size:22px;margin:36px 0 4px}
"""

def page(fonts, full_doc):
    apps = (f'<figure><span class="app" style="background:#121316;width:96px;height:96px;border-radius:22px">{ico(m, "a1", 80, "#121316", "#f4f3ef")}</span>App icon</figure>'
            f'<figure><span class="app" style="background:#f4f3ef;width:96px;height:96px;border-radius:22px;box-shadow:inset 0 0 0 1px var(--rule)">{ico(m, "a2", 80, "#f4f3ef", "#121316")}</span>Light</figure>'
            f'<figure><span class="app" style="background:#121316;width:48px;height:48px;border-radius:11px">{ico(m, "a3", 42, "#121316", "#f4f3ef")}</span>48 px</figure>'
            f'<figure><span class="app" style="background:#121316;width:32px;height:32px;border-radius:7px">{ico_s("a4", 28, "#121316", "#f4f3ef")}</span>32 px, small</figure>'
            f'<figure><span class="app" style="background:#121316;width:16px;height:16px;border-radius:4px">{ico_s("a5", 15, "#121316", "#f4f3ef")}</span>16 px, small</figure>'
            f'<figure><span class="app" style="background:#fff;width:16px;height:16px;border-radius:4px;box-shadow:inset 0 0 0 1px var(--rule)">{ico_s("a6", 15, "#fff", "#121316")}</span>16 px light</figure>'
            f'<figure><span class="app" style="background:#121316;width:16px;height:16px;border-radius:4px">{ico(m, "a7", 16, "#121316", "#f4f3ef")}</span>16 px, full</figure>')
    locks = (f'<div class="locks"><div class="lock" style="background:#121316;color:#f4f3ef">{ico(m, "l1", 44, "#121316", "#f4f3ef")}<b>Benchcarta</b></div>'
             f'<div class="lock" style="background:#fbfaf7;color:#121316;box-shadow:inset 0 0 0 1px var(--rule)">{ico(m, "l2", 44, "#fbfaf7", "#121316")}<b>Benchcarta</b></div></div>')
    body = f'''<header class="hero"><div class="in">
  <div><p class="eyebrow">Benchcarta · the mark</p><h1>Benchcarta</h1>
  <p class="lede">{html.escape(m.idea)} It began as the Open Globe, was turned to face up and closed, and now carries a third orbit on its vertical axis.</p></div>
  <div>{svg(chrome2(m, "hero", "#1a1b1f"))}</div>
</div></header>
<div class="wrap">
  <div class="panels">
    <figure class="panel p-flat" style="margin:0"><div class="art">{svg(flat2(m, "#f4f3ef", "f1", "#121316"))}</div><figcaption class="cap">Flat, dark</figcaption></figure>
    <figure class="panel p-build" style="margin:0"><div class="art" style="background:#fbfaf7">{svg(flat2(m, "#121316", "f2", "#fbfaf7"))}</div><figcaption class="cap">Flat, light</figcaption></figure>
    <figure class="panel p-chrome" style="margin:0"><div class="art">{svg(chrome2(m, "c1", "#1e2024"))}</div><figcaption class="cap">Chrome badge</figcaption></figure>
  </div>
  <h3 class="sec">With the name</h3>
  {locks}
  <h3 class="sec">Icons</h3>
  <p class="sub" style="color:var(--fg2);margin:0;max-width:70ch">From 48 px up the full mark is used. At 32 px and below a simplified version drops the bezel and thickens the lines, because the ticks blur into noise. The last chip shows the full mark at 16 px for comparison.</p>
  <div class="apps">{apps}</div>
  <h3 class="sec">Construction</h3>
  <div class="panels" style="grid-template-columns:minmax(0,2fr) minmax(0,1fr)">
    <figure class="panel p-build" style="margin:0"><div class="art">{svg(construction(m, "g1"))}</div><figcaption class="cap">Construction</figcaption></figure>
    <div class="spec">
      <div><b>Globe</b><span>Circle, radius 50, stroke 7</span></div>
      <div><b>Orbits</b><span>Three ellipses, 45 × 15, at 30°, 90° and 150° (60° apart), stroke 2.8</span></div>
      <div><b>Nucleus</b><span>The original logo's three dots, coral, purple and blue, radius 3.6, 9.5 apart on a thin line at 55% opacity. They fit inside the vertical orbit without touching it.</span></div>
      <div><b>Electrons</b><span>Radius 5.2, one on each orbit at the same point (40° along from the orbit's tip), so they keep 120° rotational symmetry: purple #A98AD4 at the top, coral #CF5F49 lower left, blue #3B8CCC lower right. On dark grounds the lighter tints are used (#C9A2F2, #E0705A, #5FA8DE). A 2.2 gap separates each from its orbit.</span></div>
      <div><b>Bezel</b><span>23 ticks every 15° from radius 58: 6 long at the quarters, 3 short between, stroke 2.2. A solid pointer replaces the tick at north.</span></div>
    </div>
  </div>
</div>'''
    head = f'<title>Benchcarta Mark</title>\n<style>\n{fonts}\n{CSS}\n</style>'
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

def export():
    out = os.path.join(HERE, "svg-final"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for k, bg, ink in (("black", "#121316", "#f4f3ef"), ("white", "#ffffff", "#121316")):
        open(os.path.join(out, f"benchcarta-mark-{k}.svg"), "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 0 140 140" width="512" height="512"><rect x="30" y="0" width="140" height="140" fill="{bg}"/>{flat2(m, ink, "x", bg)}</svg>\n')
        open(os.path.join(out, f"benchcarta-mark-{k}-transparent.svg"), "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 0 140 140" width="512" height="512">{flat2(m, ink, "x", bg)}</svg>\n')
    for k, bg, ink in (("black", "#121316", "#f4f3ef"), ("white", "#ffffff", "#121316")):
        open(os.path.join(out, f"benchcarta-small-{k}.svg"), "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="44 18 112 112" width="512" height="512"><rect x="44" y="18" width="112" height="112" fill="{bg}"/>{flat2(small, ink, "x", bg)}</svg>\n')
    open(os.path.join(out, "benchcarta-mark-chrome.svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 0 140 140" width="512" height="512"><rect x="30" y="0" width="140" height="140" fill="#1e2024"/>{chrome2(m, "x", "#1e2024")}</svg>\n')

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "final.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built final mark")
