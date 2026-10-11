"""Pole A family: the A is two meridians meeting at the north pole, the L is
cut from the same globe, and the background is a real orthographic globe.

Usage: python3 build.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from globe import Globe

HERE = os.path.dirname(os.path.abspath(__file__))
PAL = {
    "navy":  dict(name="Navy & gold", ground="#031b36", sea="#0a2a4f", grid="#5d6f5a", let="#fdffee", acc="#d4a72c", ring="#d4a72c", shade="#8c6d1f", night="#021226"),
    "earth": dict(name="Earth",       ground="#f1e7d0", sea="#e7d8b4", grid="#a8977a", let="#2e2419", acc="#b07d2a", ring="#2e2419", shade="#7f8a62", night="#d9c79f"),
}
def F(c): return f'style="fill:var(--{c})"'
def S(c): return f'style="stroke:var(--{c})"'
def stroke(d, c, w, extra=""):
    return f'<path d="{d}" fill="none" {S(c)} stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def merge(body):
    pat = re.compile(r'<([a-zA-Z]+)([^<>]*?)\sstyle="([^"]*)"([^<>]*?)\sstyle="([^"]*)"')
    while True:
        new = pat.sub(lambda m: f'<{m.group(1)}{m.group(2)} style="{m.group(3)};{m.group(5)}"{m.group(4)}', body)
        if new == body: return body
        body = new

def hatch(ang, gap, w, c):
    d = "".join(f"M-60 {k}H260" for k in range(-60, 260, int(gap*10)//10 or 1)) if gap >= 1 else ""
    d = "".join(f"M-60 {-60 + i*gap:.2f}H260" for i in range(int(320/gap)))
    return f'<g transform="rotate({ang} 100 100)">{stroke(d, c, w)}</g>'

n_id = [0]
def nid():
    n_id[0] += 1; return f"@@{n_id[0]}"

def sphere(g, style="engraved", dlon=15, dlat=15, back=False):
    """The globe ground: disc, graticule, optional back lines and shading."""
    cx, cy, r = g.cx, g.cy, g.r
    c = nid(); m = nid()
    out = f'<clipPath id="{c}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
    if style == "solid":
        out += f'<circle cx="{cx}" cy="{cy}" r="{r}" {F("sea")}/>'
    if back:
        out += stroke(g.graticule(dlon, dlat, "back"), "grid", .7, 'opacity=".45" stroke-dasharray="1.5 2.5"')
    out += stroke(g.graticule(dlon, dlat), "grid", .9 if style != "solid" else 1.1)
    if style in ("engraved", "night"):
        out += (f'<mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="0" width="200" height="200"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff"/>'
                f'<circle cx="{cx - r*.32:.2f}" cy="{cy - r*.34:.2f}" r="{r*1.05:.2f}" fill="#000"/></mask>'
                f'<g mask="url(#{m})">{hatch(45, 2.4, .75, "shade")}</g>')
    if style == "night":
        out += f'<g clip-path="url(#{c})"><path d="M{cx+r*.18:.1f} {cy-r-2}Q{cx-r*.25:.1f} {cy} {cx+r*.18:.1f} {cy+r+2}H{cx+r+4}V{cy-r-2}Z" {F("night")} opacity=".72"/></g>'
    out += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" {S("ring")} stroke-width="{2.6 if style!="solid" else 0}"/>'
    return out

def letters(g, alpha=30, lat_end=-15, cross=15, L=None, w=9, c="let", cross_c="acc"):
    """The A: meridians at +/-alpha from the pole down to lat_end, crossbar on a parallel.
    L: legs list for globe.path, drawn in the same stroke as the A's left leg when it joins."""
    a_left = [("m", -alpha, lat_end, 90)] if L is None else L + [("m", -alpha, lat_end, 90)]
    d = g.path(a_left + [("m", alpha, 90, lat_end)])
    return stroke(d, c, w) + stroke(g.parallel(cross, -alpha, alpha), cross_c, w*.8)

def bezel(r=92, c="ring"):
    t = "".join(f"M{100 + (r-9)*math.cos(math.radians(i*5)):.2f} {100 + (r-9)*math.sin(math.radians(i*5)):.2f}L{100 + (r-9+(6 if i%6==0 else 3))*math.cos(math.radians(i*5)):.2f} {100 + (r-9+(6 if i%6==0 else 3))*math.sin(math.radians(i*5)):.2f}" for i in range(72))
    return (f'<circle cx="100" cy="100" r="{r}" fill="none" {S(c)} stroke-width="1"/>' + stroke(t, c, .9) +
            f'<circle cx="100" cy="100" r="{r-9}" fill="none" {S(c)} stroke-width="1.8"/>')

def star(x, y, R, c="acc", n=5, k=.42):
    pts = [(x + (R if i % 2 == 0 else R*k)*math.cos(math.radians(-90 + i*180/n)), y + (R if i % 2 == 0 else R*k)*math.sin(math.radians(-90 + i*180/n))) for i in range(2*n)]
    return f'<path d="M{" L".join(f"{a:.2f} {b:.2f}" for a, b in pts)}Z" {F(c)}/>'

LIMB_L = [("m", -75, 45, -15), ("p", -15, -75, -30)]

V = []
def variant(name, idea, full, small):
    V.append(dict(n=len(V)+1, name=name, idea=idea, full=merge(full), small=merge(small)))

# 1 Grid ligature: every stroke of L and A is a line of a 15-degree graticule
g = Globe(r=74, tilt=26, lon0=-12)
variant("Graticule Ligature",
        "Both letters are lines of the globe's own 15° grid. The L comes down the 75°W meridian and turns along 15°S, then climbs the A's left meridian to the pole in one unbroken stroke. The crossbar is 15°N. The letters were always on the map.",
        sphere(g) + letters(g, L=LIMB_L) + f'<circle cx="{g.xy(90,0)[0]:.2f}" cy="{g.xy(90,0)[1]:.2f}" r="4" {F("acc")}/>',
        sphere(Globe(r=88, tilt=26, lon0=-12), "solid", 30, 30) + letters(Globe(r=88, tilt=26, lon0=-12), L=LIMB_L, w=17))

# 2 Same, as a solid sphere with a back-side graticule showing through
variant("Glass Globe",
        "The same ligature on a glass globe: you can see the far side's grid through it, faint and dashed, like an armillary sphere. The letters sit on the near face.",
        sphere(g, "solid", back=True) + letters(g, L=LIMB_L) + f'<circle cx="{g.xy(90,0)[0]:.2f}" cy="{g.xy(90,0)[1]:.2f}" r="4" {F("acc")}/>',
        sphere(Globe(r=88, tilt=26, lon0=-12), "solid", 30, 30) + letters(Globe(r=88, tilt=26, lon0=-12), L=LIMB_L, w=17))

# 3 Compass rose at the pole: the apex of the A is the north point of a rose
g3 = Globe(r=74, tilt=26, lon0=-12)
px3, py3, _ = g3.xy(90, 0)
def rose(x, y, L, W, c1="acc", c2="ground", w=.9):
    out = ""
    for i, (l, ww) in enumerate([(L, W), (L*.55, W*.8)] * 1):
        pass
    for i in range(8):
        a = -90 + i*45; ln = L if i % 2 == 0 else L*.5; wd = W if i % 2 == 0 else W*.75
        tip = (x + ln*math.cos(math.radians(a)), y + ln*math.sin(math.radians(a)))
        l = (x + wd*math.cos(math.radians(a-90)), y + wd*math.sin(math.radians(a-90)))
        r = (x + wd*math.cos(math.radians(a+90)), y + wd*math.sin(math.radians(a+90)))
        out += f'<path d="M{x:.2f} {y:.2f}L{tip[0]:.2f} {tip[1]:.2f}L{l[0]:.2f} {l[1]:.2f}Z" {F(c1)}/>'
        out += f'<path d="M{x:.2f} {y:.2f}L{tip[0]:.2f} {tip[1]:.2f}L{r[0]:.2f} {r[1]:.2f}Z" {F(c2)} {S(c1)} stroke-width="{w}" stroke-linejoin="round"/>'
    return out
rhumbs = "".join(stroke(f"M{px3:.2f} {py3:.2f}L{px3 + 120*math.cos(math.radians(a)):.2f} {py3 + 120*math.sin(math.radians(a)):.2f}", "acc", .5, 'opacity=".55"') for a in range(0, 360, 15))
variant("Rose at the Pole",
        "The ligature globe with a compass rose set on the north pole, where the A's two meridians meet, and rhumb lines running out across the sky as on a sea chart. True north is the top of the A.",
        f'<clipPath id="@@r"><rect width="200" height="200"/></clipPath><g clip-path="url(#@@r)">{rhumbs}</g>' + f'<circle cx="100" cy="100" r="76" {F("ground")}/>' +
        sphere(g3) + letters(g3, L=LIMB_L) + rose(px3, py3, 22, 4.2),
        sphere(Globe(r=84, tilt=26, lon0=-12, cy=108), "solid", 30, 30) + letters(Globe(r=84, tilt=26, lon0=-12, cy=108), L=LIMB_L, w=16) +
        rose(*Globe(r=84, tilt=26, lon0=-12, cy=108).xy(90, 0)[:2], 26, 6, w=1.6))

# 4 Coordinate corner: the L is a surveyor's corner mark on the globe, pinning a location
g4 = Globe(r=74, tilt=26)
cx4, cy4, _ = g4.xy(-30, 48)
corner = g4.path([("m", 6, -20, -44), ("p", -44, 6, 40)])
variant("Coordinate Corner",
        "The A is Pole A. The L is a gold corner mark, drawn along a meridian and a parallel, the kind a surveyor uses to pin a point. The L marks where your lab is.",
        sphere(g4) + letters(g4, alpha=32, lat_end=-8, cross=18) + stroke(corner, "acc", 6) +
        f'<circle cx="{g4.xy(-32, 22)[0]:.2f}" cy="{g4.xy(-32, 22)[1]:.2f}" r="5" {F("acc")}/>',
        sphere(Globe(r=88, tilt=26), "solid", 30, 30) + letters(Globe(r=88, tilt=26), alpha=32, lat_end=-8, cross=18, w=17) +
        stroke(Globe(r=88, tilt=26).path([("m", 6, -20, -46), ("p", -46, 6, 44)]), "acc", 13))

# 5 Desk globe on an L-shaped stand
g5 = Globe(cx=108, cy=86, r=60, tilt=26)
ring = f'<path d="M{108-66*math.cos(math.radians(60)):.1f} {86-66*math.sin(math.radians(60)):.1f}A66 66 0 0 0 {108-66*math.cos(math.radians(60)):.1f} {86+66*math.sin(math.radians(60)):.1f}" fill="none" {S("acc")} stroke-width="4"/>'
variant("Globe on an L",
        "A desk globe showing Pole A, held by a cantilever stand shaped like an L. The post and the foot are the L's stem and base, so the L literally holds up the atlas.",
        sphere(g5) + letters(g5, alpha=32, lat_end=-8, cross=18, w=7.5) + ring +
        stroke("M42 30V176H170", "let", 9) + stroke("M42 86H50", "let", 6) + stroke("M30 182H182", "ring", 1.4) + stroke("M42 30H52", "let", 6),
        sphere(Globe(cx=114, cy=84, r=64, tilt=26), "solid", 30, 30) + letters(Globe(cx=114, cy=84, r=64, tilt=26), alpha=32, lat_end=-8, cross=18, w=14) +
        stroke("M26 18V184H186", "let", 18))

# 6 Seal: the graticule ligature inside an instrument bezel with stars
g6 = Globe(r=66, tilt=26, lon0=-12)
variant("Pole Seal",
        "The ligature globe set into a graduated bezel, with a star at the pole and two at the equator. It works as a seal for print, stickers and certificates.",
        bezel() + sphere(g6) + letters(g6, L=LIMB_L, w=8) + star(*g6.xy(90, 0)[:2], 6.5) + star(18, 100, 3.6) + star(182, 100, 3.6),
        f'<circle cx="100" cy="100" r="96" fill="none" {S("ring")} stroke-width="8"/>' + sphere(Globe(r=78, tilt=26, lon0=-12), "solid", 30, 30) +
        letters(Globe(r=78, tilt=26, lon0=-12), L=LIMB_L, w=15))

# 7 Day and night: half the globe in shadow, the letters catch the light
g7 = Globe(r=74, tilt=26, lon0=-12)
variant("Terminator",
        "The globe is half in night, with the shadow line cutting through the letters, as the planet looks from space. The A's pole sits in daylight.",
        sphere(g7, "night") + letters(g7, L=LIMB_L) + f'<circle cx="{g7.xy(90,0)[0]:.2f}" cy="{g7.xy(90,0)[1]:.2f}" r="4" {F("acc")}/>' +
        "".join(f'<circle cx="{x}" cy="{y}" r="{r}" {F("acc")}/>' for x, y, r in [(176, 30, 1.6), (186, 62, 1), (160, 176, 1.2), (20, 40, 1), (28, 170, 1.4)]),
        sphere(Globe(r=88, tilt=26, lon0=-12), "solid", 30, 30) +
        f'<clipPath id="@@t"><circle cx="100" cy="100" r="88"/></clipPath><g clip-path="url(#@@t)"><path d="M116 8Q78 100 116 192H200V8Z" {F("night")}/></g>' +
        letters(Globe(r=88, tilt=26, lon0=-12), L=LIMB_L, w=17))

# 8 Bold monoline: fewer grid lines, heavier letters, built for small sizes first
g8 = Globe(r=80, tilt=26, lon0=-12)
variant("Bold Globe",
        "Built small-first: a 30° grid and heavy letters, so the mark survives as a 16-pixel favicon and still reads as a globe on a billboard.",
        sphere(g8, "solid", 30, 30) + letters(g8, L=LIMB_L, w=13) + f'<circle cx="{g8.xy(90,0)[0]:.2f}" cy="{g8.xy(90,0)[1]:.2f}" r="6" {F("acc")}/>',
        sphere(Globe(r=92, tilt=26, lon0=-12), "solid", 45, 45) + letters(Globe(r=92, tilt=26, lon0=-12), L=LIMB_L, w=20))

# ---------------------------------------------------------------- page
def svg(body, size, key):
    return f'<svg viewBox="0 0 200 200" width="{size}" height="{size}" aria-hidden="true">{body.replace("@@", f"p{key}-")}</svg>'

def export():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for k, p in PAL.items():
        for v in V:
            for kind in ("full", "small"):
                body = v[kind].replace("@@", "p")
                body = re.sub(r'style="([^"]*)"', lambda m: " ".join(f'{a}="{p[b]}"' for a, b in re.findall(r'(fill|stroke):var\(--(\w+)\)', m.group(1))), body)
                slug = re.sub(r"[^a-z0-9]+", "-", v["name"].lower()).strip("-")
                with open(os.path.join(out, f"{v['n']:02d}-{slug}-{k}{'' if kind=='full' else '-small'}.svg"), "w") as fh:
                    fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="400" height="400"><title>{html.escape(v["name"])}</title>'
                             f'<rect width="200" height="200" fill="{p["ground"]}"/><g transform="translate(10 10) scale(.9)">{body}</g></svg>\n')

def tokens(p): return ";".join(f"--{k}:{v}" for k, v in p.items() if k != "name")

CSS = """
/* Layout: one hero plate for the lead version, then a catalogue of the family, both palettes side by side. */
:root{--bg:#f4efe3;--surface:#fbf8f0;--fg:#231c14;--fg2:#6b5f4f;--rule:#dfd4bd;--accent:#8e4f2f;
  --sans:'Atlas Text',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;--serif:'Cormorant Garamond','Iowan Old Style',Georgia,serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0b1420;--surface:#111d2c;--fg:#ece6d6;--fg2:#a49a86;--rule:#26364a;--accent:#d4a72c;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0b1420;--surface:#111d2c;--fg:#ece6d6;--fg2:#a49a86;--rule:#26364a;--accent:#d4a72c;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-inline:clamp(16px,4vw,40px);padding-block:44px 72px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg2);margin:0 0 10px}
h1{font-family:var(--serif);font-weight:500;font-style:italic;font-size:clamp(40px,6vw,70px);line-height:.98;margin:0 0 14px;text-wrap:balance}
.lede{color:var(--fg2);max-width:62ch;margin:0}
.hero{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:20px;margin:28px 0 8px}
.hero .tile{border-radius:4px}
.hero-side{display:grid;grid-template-rows:auto auto 1fr;gap:20px;min-width:0}
.hero-side .tile{aspect-ratio:auto;height:100%}
.hero-pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.apps{display:flex;gap:14px;align-items:flex-end;flex-wrap:wrap}
.apps figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:6px;font-size:11px;color:var(--fg2)}
.app{display:grid;place-items:center;background:var(--ground)}
.nav{display:flex;align-items:center;gap:12px;padding:14px 18px;background:var(--ground);border-radius:4px;color:var(--let)}
.nav b{font-weight:400;font-size:20px;letter-spacing:-.01em}
.nav span{margin-left:auto;font-size:13px;opacity:.7}
.cap{font-size:12px;color:var(--fg2);letter-spacing:.06em;text-transform:uppercase;margin:0 0 6px}
h2{font-family:var(--serif);font-weight:500;font-size:30px;margin:52px 0 6px}
.sub{color:var(--fg2);margin:0 0 18px;max-width:62ch}
.plates{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}
.plate{background:var(--surface);border:1px solid var(--rule);border-radius:4px;display:flex;flex-direction:column;min-width:0}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--rule)}
.tile{aspect-ratio:1/1;max-width:100%;display:grid;place-items:center;background:var(--ground)}
.tile svg{width:90%;height:90%}
.meta{padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px;flex:1}
.row{display:flex;align-items:baseline;gap:10px}
.no{font-family:var(--serif);font-style:italic;font-size:18px;color:var(--fg2)}
h3{margin:0;font-family:var(--serif);font-weight:600;font-size:22px;line-height:1.1}
.why{margin:0;color:var(--fg2);font-size:13.5px;flex:1}
.small{display:flex;gap:6px;align-items:center;font-size:11px;color:var(--fg2)}
.chip{display:grid;place-items:center;border-radius:7px;background:var(--ground)}
.c32{width:32px;height:32px}.c16{width:16px;height:16px;border-radius:4px}
@media (max-width:820px){.hero{grid-template-columns:minmax(0,1fr)}}
"""

def page(fonts, full_doc):
    lead = V[0]
    navy, earth = tokens(PAL["navy"]), tokens(PAL["earth"])
    hero = f'''<div class="hero">
  <div class="tile" style="{navy}">{svg(lead["full"], 520, "h1")}</div>
  <div class="hero-side">
    <div class="hero-pair"><div class="tile" style="{earth}">{svg(lead["full"], 240, "h2")}</div><div class="tile" style="{navy}">{svg(V[5]["full"], 240, "h3")}</div></div>
    <div><p class="cap">In use</p>
      <div class="nav" style="{navy}">{svg(lead["small"], 30, "n1")}<b>Lab Atlas</b><span>Find a lab</span></div>
      <div class="nav" style="{earth};margin-top:10px">{svg(lead["small"], 30, "n2")}<b>Lab Atlas</b><span>Find a lab</span></div></div>
    <div class="apps">
      <figure><span class="app" style="{navy};width:84px;height:84px;border-radius:20px">{svg(lead["small"], 66, "a1")}</span>App icon</figure>
      <figure><span class="app" style="{earth};width:84px;height:84px;border-radius:20px">{svg(lead["small"], 66, "a2")}</span>App icon</figure>
      <figure><span class="app" style="{navy};width:32px;height:32px;border-radius:7px">{svg(lead["small"], 28, "a3")}</span>32 px</figure>
      <figure><span class="app" style="{navy};width:16px;height:16px;border-radius:4px">{svg(lead["small"], 15, "a4")}</span>16 px</figure>
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
    body = f'''<div class="wrap">
  <p class="eyebrow">Lab Atlas · round three</p>
  <h1>Pole A, with its L, on a real globe</h1>
  <p class="lede">The A is two meridians meeting at the north pole, with a parallel as its crossbar. The globe is a true orthographic projection seen from above the equator, so the pole sits on its face and the meridians converge into the A on their own. Each variation below finds the L on the same globe.</p>
  {hero}
  <h2>The family</h2>
  <p class="sub">Eight ways to bring in the L. Every card shows the navy-and-gold and the earth palette, and the simplified version at 32 and 16 pixels.</p>
  <main class="plates">{plates}</main>
</div>'''
    head = ('<title>Lab Atlas Pole A</title>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap">\n'
            f'<style>\n{fonts}\n{CSS}\n</style>')
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    open(os.path.join(HERE, "index.html"), "w").write(page(fonts, True))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(page(fonts, False))
    print("built", len(V))
