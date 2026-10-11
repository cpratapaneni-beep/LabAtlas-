"""Atlas moth round: the atlas moth combined with the Pole A globe.

Usage: python3 build.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pole-a"))
import build as PA
from globe import Globe
from build import F, S, stroke, merge, sphere, letters, LIMB_L

MOTH = {
    "navy":  dict(mwing="#cf8e30", mwing2="#a8622a", medge="#1a1009", mband="#f3e2bf", mwin="#fdffee", mhook="#ebb75e", mbody="#2a1a0e"),
    "earth": dict(mwing="#c47a2c", mwing2="#9a5320", medge="#3a2418", mband="#f3e2bf", mwin="#fbf1dc", mhook="#e8a54a", mbody="#3a2418"),
}
PAL = {k: dict(PA.PAL[k], **MOTH[k]) for k in PA.PAL}
def tokens(p): return ";".join(f"--{k}:{v}" for k, v in p.items() if k != "name")

FW = "M104 84C126 58 156 36 182 30C188 34 188 42 181 48C180 64 177 80 170 96C150 102 126 104 104 104Z"
HW = "M104 106C130 103 158 106 170 120C175 142 162 166 138 172C122 175 110 162 104 142Z"

def mirror(b): return b + f'<g transform="translate(200 0) scale(-1 1)">{b}</g>'

def nest(d, ax, ay, scales):
    return "".join(f'<path d="{d}" transform="translate({ax*(1-s):.2f} {ay*(1-s):.2f}) scale({s})" fill="none" {S("medge")} stroke-width="{.9/s:.2f}"/>' for s in scales)

def antennae():
    a = stroke("M103 66C110 50 120 40 132 34", "mbody", 2)
    for i in range(8):
        t = (i+1)/9; x = 103 + 29*t; y = 66 - 32*t - 6*math.sin(math.pi*t)
        a += stroke(f"M{x:.1f} {y:.1f}l-3 -4M{x:.1f} {y:.1f}l4 1", "mbody", 1.1)
    return a

def moth(pattern="contour", windows=True, uid="m"):
    """The atlas moth, drawn on its own 200 grid with its body centred on (100, 104)."""
    right = ""
    for d, fill, anchor, k in ((FW, "mwing", (106, 96), "f"), (HW, "mwing2", (106, 118), "h")):
        right += f'<path d="{d}" {F(fill)}/>'
        if pattern == "contour":
            right += f'<clipPath id="@@{uid}{k}"><path d="{d}"/></clipPath><g clip-path="url(#@@{uid}{k})">{nest(d, *anchor, (.82, .66, .5))}</g>'
    right += stroke("M108 94C128 84 150 74 176 66", "mband", 3.2) + stroke("M108 120C126 118 146 122 164 134", "mband", 3)
    if windows:
        right += f'<path d="M140 74L152 68L150 82Z" {F("mwin")} {S("medge")} stroke-width="1"/><path d="M128 134L142 130L136 146Z" {F("mwin")} {S("medge")} stroke-width="1"/>'
    right += f'<path d="M174 34C186 30 189 38 183 47C180 44 176 40 174 34Z" {F("mhook")}/><circle cx="181" cy="38" r="1.8" {F("medge")}/>'
    right += f'<path d="{FW}" fill="none" {S("medge")} stroke-width="2.2" stroke-linejoin="round"/><path d="{HW}" fill="none" {S("medge")} stroke-width="2.2" stroke-linejoin="round"/>'
    body = (f'<ellipse cx="100" cy="106" rx="7.5" ry="36" {F("mbody")}/>'
            + "".join(f'<path d="M93.5 {y}Q100 {y+3} 106.5 {y}" fill="none" {S("mwing")} stroke-width="1.2" opacity=".7"/>' for y in range(96, 136, 7))
            + f'<circle cx="100" cy="68" r="8" {F("mbody")}/><circle cx="96.5" cy="66" r="2" {F("mwin")}/><circle cx="103.5" cy="66" r="2" {F("mwin")}/>')
    return mirror(right + antennae()) + body

def moth_icon(windows=True):
    fw = "M104 82C128 52 160 30 188 24C194 30 192 40 184 46C182 66 178 84 170 100C150 106 126 108 104 108Z"
    hw = "M104 110C132 108 162 112 174 128C178 152 164 176 138 182C120 184 110 170 104 148Z"
    r = f'<path d="{fw}" {F("mwing")}/><path d="{hw}" {F("mwing2")}/>'
    if windows: r += f'<path d="M136 70L154 62L150 84Z" {F("mwin")}/><path d="M126 136L146 130L136 152Z" {F("mwin")}/>'
    return mirror(r) + f'<ellipse cx="100" cy="108" rx="10" ry="40" {F("mbody")}/><circle cx="100" cy="64" r="10" {F("mbody")}/>'

def place(body, x, y, s, rot=0):
    """Put a moth (body centre 100,104) at x, y with scale s."""
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot}) scale({s}) translate(-100 -104)">{body}</g>'

V = []
def variant(name, idea, full, small):
    V.append(dict(n=len(V)+1, name=name, idea=idea, full=merge(full), small=merge(small)))

LEAD = dict(r=74, tilt=26, lon0=-22)

# 1 Moth at the pole
g = Globe(**LEAD); px, py, _ = g.xy(90, 0)
gs = Globe(r=82, tilt=26, lon0=-22, cy=110); sx, sy, _ = gs.xy(90, 0)
variant("Moth at the Pole",
        "The Pole A globe with an atlas moth landed on the north pole, right where the A's two meridians meet. Atlas the titan, the atlas of maps and the atlas moth come together in one mark.",
        sphere(g) + letters(g, L=LIMB_L) + place(moth(uid="a"), px, py - 6, .3),
        sphere(gs, "solid", 30, 30) + letters(gs, L=LIMB_L, w=15) + place(moth_icon(), sx, sy - 10, .42))

# 2 Atlas wings: the windows in the forewings are an L and an A, and the wings carry a map grid
def l_window():
    return f'<path d="M46 56H54V77H67V85H46Z" {F("mwin")} {S("medge")} stroke-width="1.2" stroke-linejoin="round"/>'
def a_window():
    return (f'<path d="M146 52L161 86H131Z" {F("mwin")} {S("medge")} stroke-width="1.2" stroke-linejoin="round"/>'
            f'<path d="M146 64.5L150.6 75H141.4Z" {F("mwing")}/><path d="M139.6 86H152.4L149 78.5H143Z" {F("mwing")}/>')
def map_wings(uid):
    gw = Globe(cx=100, cy=104, r=96, tilt=20)
    grid = stroke(gw.graticule(15, 15), "medge", 1.1, 'opacity=".8"')
    clipd = FW + " " + HW
    mir = f'<g transform="translate(200 0) scale(-1 1)"><path d="{FW}"/><path d="{HW}"/></g>'
    return f'<clipPath id="@@{uid}w"><path d="{FW}"/><path d="{HW}"/><path d="{FW}" transform="translate(200 0) scale(-1 1)"/><path d="{HW}" transform="translate(200 0) scale(-1 1)"/></clipPath><g clip-path="url(#@@{uid}w)">{grid}</g>'
def atlas_wings(uid, big=False):
    m = moth(pattern="grid", windows=False, uid=uid)
    # insert the map grid just after the wing fills by layering: fills, grid, then the rest is fine on top
    return m + map_wings(uid) + l_window() + a_window()
variant("Atlas Wings",
        "The atlas moth is said to be named for the map-like patterns on its wings. Here its wings carry a real globe grid, and the clear windows in its forewings are cut as an L and an A.",
        atlas_wings("b"),
        moth_icon(windows=False) + f'<path d="M36 50H48V80H66V92H36Z" {F("mwin")}/><path d="M150 40L172 92H128Z" {F("mwin")}/><path d="M150 59L156.5 74H143.5Z" {F("mwing")}/><path d="M139 92H161L156 81H144Z" {F("mwing")}/>')

# 3 Moth seal
seal_g = Globe(r=78, tilt=26, lon0=-22)
variant("Moth Seal",
        "The atlas moth spread across a globe and set into a graduated bezel, with a star at each quarter. It is the emblem version, for print, merchandise and the site footer.",
        PA.bezel() + f'<clipPath id="@@sc"><circle cx="100" cy="100" r="82"/></clipPath><g clip-path="url(#@@sc)">{stroke(seal_g.graticule(15, 15), "grid", .8)}</g>' +
        place(moth(uid="c"), 100, 104, .8) + "".join(PA.star(*p, 3.6) for p in [(100, 12), (188, 100), (100, 188), (12, 100)]),
        f'<circle cx="100" cy="100" r="94" fill="none" {S("ring")} stroke-width="8"/>' + place(moth_icon(), 100, 104, .86))

# 4 Drawn to the light: the moth flies a dotted path toward the glowing Pole A globe
g4 = Globe(cx=116, cy=110, r=58, tilt=26, lon0=-22)
glow = "".join(stroke(f"M{116 + 64*math.cos(math.radians(a)):.1f} {110 + 64*math.sin(math.radians(a)):.1f}L{116 + (80 if i % 2 else 72)*math.cos(math.radians(a)):.1f} {110 + (80 if i % 2 else 72)*math.sin(math.radians(a)):.1f}", "acc", 1.2) for i, a in enumerate(range(0, 360, 10)))
variant("Drawn to the Light",
        "Moths are drawn to light, and students are drawn to research. The moth follows a dotted flight path toward the glowing Pole A globe.",
        glow + sphere(g4) + letters(g4, L=LIMB_L, w=7.5) +
        stroke("M40 58C30 90 70 120 64 84C60 60 40 70 48 100", "acc", 1.8, 'stroke-dasharray="0.1 5"') + place(moth(uid="d"), 38, 44, .26, -24),
        sphere(Globe(cx=120, cy=118, r=72, tilt=26, lon0=-22), "solid", 30, 30) + letters(Globe(cx=120, cy=118, r=72, tilt=26, lon0=-22), L=LIMB_L, w=13) +
        place(moth_icon(), 44, 44, .42, -24))

# 5 Hemisphere wings: the forewings are two globes, the left showing the L, the right the A
gl = Globe(cx=60, cy=78, r=40, tilt=26, lon0=0)
gr = Globe(cx=140, cy=78, r=40, tilt=26, lon0=0)
hw_r = "M104 112C130 110 152 118 156 138C158 156 144 172 126 172C112 172 106 156 104 140Z"
def hemi_moth(w=6, icon=False):
    hw = f'<path d="{hw_r}" {F("mwing2")}/>' + ("" if icon else stroke("M108 124C122 124 138 130 148 142", "mband", 2.4) + f'<path d="M122 140L134 136L130 150Z" {F("mwin")}/>' + f'<path d="{hw_r}" fill="none" {S("medge")} stroke-width="2"/>')
    out = mirror(hw)
    out += sphere(gl, "solid", 30 if icon else 15, 30 if icon else 15) + sphere(gr, "solid", 30 if icon else 15, 30 if icon else 15)
    out += f'<circle cx="60" cy="78" r="40" fill="none" {S("mwing")} stroke-width="{6 if icon else 4}"/><circle cx="140" cy="78" r="40" fill="none" {S("mwing")} stroke-width="{6 if icon else 4}"/>'
    out += stroke(gl.path([("m", -38, 72, -30), ("p", -30, -38, 42)]), "let", w)
    out += letters(gr, alpha=32, lat_end=-25, cross=12, w=w)
    out += (f'<ellipse cx="100" cy="108" rx="{7 if not icon else 10}" ry="38" {F("mbody")}/><circle cx="100" cy="66" r="{8 if not icon else 11}" {F("mbody")}/>')
    if not icon: out += mirror(antennae())
    return out
variant("Hemisphere Wings",
        "The two-hemisphere world map from old atlas title pages becomes the moth's forewings. The left hemisphere carries the L and the right one carries Pole A, so the moth spells LA as it opens its wings.",
        hemi_moth(), hemi_moth(w=11, icon=True))

# 6 Resting moth A, perched on an L-shaped twig
delta = "M100 40L158 150Q100 138 42 150Z"
def resting(icon=False):
    out = stroke("M30 26V172H178", "mbody", 10 if icon else 7)
    if not icon:
        out += f'<path d="M30 70C42 62 52 64 58 72C48 78 38 78 30 70Z" {F("shade")}/><path d="M30 120C20 112 12 114 8 122C16 128 24 128 30 120Z" {F("shade")}/>'
    out += f'<path d="{delta}" {F("mwing")}/>'
    if not icon:
        out += f'<clipPath id="@@rd"><path d="{delta}"/></clipPath><g clip-path="url(#@@rd)">{nest(delta, 100, 128, (.8, .6, .4))}</g>'
        out += stroke("M64 108Q100 98 136 108", "mband", 4) + f'<path d="M80 130L90 122L92 136Z" {F("mwin")}/><path d="M120 130L110 122L108 136Z" {F("mwin")}/>'
        out += f'<path d="{delta}" fill="none" {S("medge")} stroke-width="2.4" stroke-linejoin="round"/>'
        out += stroke("M97 44C88 30 80 24 70 22M103 44C112 30 120 24 130 22", "mbody", 1.8)
    else:
        out += stroke("M58 112Q100 100 142 112", "mwin", 9)
    out += f'<path d="M100 44V150" {S("mbody")} stroke-width="{6 if icon else 4}" stroke-linecap="round"/>'
    out += f'<path d="M58 162L52 172M142 162L148 172" {S("mbody")} stroke-width="0"/>'
    return out
variant("Resting Moth",
        "A moth at rest folds its wings into a tent, which is an A, with its wing band as the crossbar. It is resting on a branch bent into an L.",
        resting(), resting(True))

# ---------------------------------------------------------------- page
def svg(body, size, key): return f'<svg viewBox="0 0 200 200" width="{size}" height="{size}" aria-hidden="true">{body.replace("@@", f"m{key}-")}</svg>'

def export():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for k, p in PAL.items():
        for v in V:
            for kind in ("full", "small"):
                body = v[kind].replace("@@", "m")
                body = re.sub(r'style="([^"]*)"', lambda m: " ".join(f'{a}="{p[b]}"' for a, b in re.findall(r'(fill|stroke):var\(--(\w+)\)', m.group(1))), body)
                slug = re.sub(r"[^a-z0-9]+", "-", v["name"].lower()).strip("-")
                with open(os.path.join(out, f"{v['n']:02d}-{slug}-{k}{'' if kind=='full' else '-small'}.svg"), "w") as fh:
                    fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="400" height="400"><title>{html.escape(v["name"])}</title>'
                             f'<rect width="200" height="200" fill="{p["ground"]}"/><g transform="translate(10 10) scale(.9)">{body}</g></svg>\n')

def page(fonts, full_doc):
    nv, ea = tokens(PAL["navy"]), tokens(PAL["earth"])
    lead = V[0]
    hero = f'''<div class="hero">
  <div class="tile" style="{nv}">{svg(lead["full"], 520, "h1")}</div>
  <div class="hero-side">
    <div class="hero-pair"><div class="tile" style="{ea}">{svg(lead["full"], 240, "h2")}</div><div class="tile" style="{nv}">{svg(V[1]["full"], 240, "h3")}</div></div>
    <div><p class="cap">In use</p>
      <div class="nav" style="{nv}">{svg(lead["small"], 30, "n1")}<b>Lab Atlas</b><span>Find a lab</span></div>
      <div class="nav" style="{ea};margin-top:10px">{svg(lead["small"], 30, "n2")}<b>Lab Atlas</b><span>Find a lab</span></div></div>
    <div class="apps">
      <figure><span class="app" style="{nv};width:84px;height:84px;border-radius:20px">{svg(lead["small"], 66, "a1")}</span>App icon</figure>
      <figure><span class="app" style="{ea};width:84px;height:84px;border-radius:20px">{svg(lead["small"], 66, "a2")}</span>App icon</figure>
      <figure><span class="app" style="{nv};width:32px;height:32px;border-radius:7px">{svg(lead["small"], 28, "a3")}</span>32 px</figure>
      <figure><span class="app" style="{nv};width:16px;height:16px;border-radius:4px">{svg(lead["small"], 15, "a4")}</span>16 px</figure>
    </div>
  </div>
</div>'''
    plates = ""
    for v in V:
        tiles = "".join(f'<div class="tile" style="{tokens(p)}">{svg(v["full"], 200, f"{v["n"]}{k}")}</div>' for k, p in PAL.items())
        chips = "".join(f'<span class="chip c32" style="{tokens(p)}">{svg(v["small"], 28, f"{v["n"]}{k}s")}</span><span class="chip c16" style="{tokens(p)}">{svg(v["small"], 14, f"{v["n"]}{k}t")}</span>' for k, p in PAL.items())
        plates += f'''<article class="plate"><div class="pair">{tiles}</div><div class="meta">
  <div class="row"><span class="no">{v["n"]:02d}</span><h3>{html.escape(v["name"])}</h3></div>
  <p class="why">{html.escape(v["idea"])}</p><div class="small">Small{chips}</div></div></article>\n'''
    plain = "".join(f'<div class="tile" style="{tokens(p)}">{svg(moth(uid=f"p{k}"), 200, f"pl{k}")}</div>' for k, p in PAL.items())
    body = f'''<div class="wrap">
  <p class="eyebrow">Lab Atlas · round four</p>
  <h1>The atlas moth meets Pole A</h1>
  <p class="lede">The atlas moth is one of the largest moths in the world, and its name is often traced to the map-like patterns on its wings. Here it joins the Pole A globe: perched on the pole, carrying the map on its wings, or opening its wings to spell LA.</p>
  {hero}
  <h2>Six ways to bring in the moth</h2>
  <p class="sub">Each card shows the navy-and-gold and the earth palette, and the simplified version at 32 and 16 pixels.</p>
  <main class="plates">{plates}</main>
  <h2>The moth on its own</h2>
  <p class="sub">The character drawing everything above is built from. Its forewing tips are shaped like snake heads, as on the real atlas moth.</p>
  <div class="plates"><article class="plate"><div class="pair">{plain}</div></article></div>
</div>'''
    head = ('<title>Lab Atlas Moth</title>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap">\n'
            f'<style>\n{fonts}\n{PA.CSS}\n</style>')
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "index.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built", len(V))
