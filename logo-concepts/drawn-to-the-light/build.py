"""Drawn to the Light: a side-view atlas moth flying in front of the glowing Pole A globe.

Usage: python3 build.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pole-a"))
import build as PA
from globe import Globe
from build import F, S, stroke, merge, sphere, letters, LIMB_L

spec = importlib.util.spec_from_file_location("mothround", os.path.join(HERE, "..", "moth", "build.py"))
MR = importlib.util.module_from_spec(spec); spec.loader.exec_module(MR)
PAL = MR.PAL
tokens = MR.tokens

# ---------------------------------------------------------------- side-view moth (faces right, no face)
# Wings raised and swept back over a stout body. The far forewing is the near one, turned a little forward.
FORE = "M121 95C122 70 110 40 92 21C86 30 72 46 54 64C70 82 86 96 97 104Z"
HOOK = "M92 22C88 14 96 9 102 14C99 17 95 19 92 22Z"
HIND = "M100 104C84 92 62 84 44 88C40 102 50 118 66 123C80 126 94 118 102 110Z"
BODY = "M106 100C92 100 76 108 64 118C60 123 64 129 71 127C86 122 100 116 110 112Z"

def turn(d, dx, dy, ang, cx, cy):
    nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", d)]
    a = math.radians(ang); out = []
    for x, y in zip(nums[::2], nums[1::2]):
        x0, y0 = x - cx, y - cy
        out.append((cx + x0*math.cos(a) - y0*math.sin(a) + dx, cy + x0*math.sin(a) + y0*math.cos(a) + dy))
    it = iter(out)
    return re.sub(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", lambda m: "{:.2f} {:.2f}".format(*next(it)), d)

FAR_FORE = turn(FORE, 13, -2, 9, 121, 95)
FAR_HOOK = turn(HOOK, 13, -2, 9, 121, 95)

def nest(d, ax, ay, scales, c="medge", w=.9):
    return "".join(f'<path d="{d}" transform="translate({ax*(1-s):.2f} {ay*(1-s):.2f}) scale({s})" fill="none" {S(c)} stroke-width="{w/s:.2f}"/>' for s in scales)

def antenna(d, ticks, flip=1):
    out = stroke(d, "mbody", 1.8)
    for (x, y) in ticks:
        out += stroke(f"M{x:.1f} {y:.1f}l{3*flip} -3.5M{x:.1f} {y:.1f}l-3.6 -1.4", "mbody", 1)
    return out

def side_moth(uid, halo=True, detail=True):
    out = ""
    if halo:
        out += "".join(f'<path d="{d}" {F("ground")} {S("ground")} stroke-width="7" stroke-linejoin="round"/>' for d in (FAR_FORE, FAR_HOOK, FORE, HOOK, HIND, BODY))
        out += f'<ellipse cx="114" cy="103" rx="16" ry="13.5" {F("ground")}/><circle cx="129" cy="98" r="9.5" {F("ground")}/>'
    # far forewing, peeking past the near one
    out += f'<path d="{FAR_FORE}" {F("mwing2")} {S("medge")} stroke-width="1.6" stroke-linejoin="round"/><path d="{FAR_HOOK}" {F("mwing2")} {S("medge")} stroke-width="1.2" stroke-linejoin="round"/>'
    # hindwing
    out += f'<path d="{HIND}" {F("mwing2")}/>'
    if detail:
        out += f'<clipPath id="@@{uid}h"><path d="{HIND}"/></clipPath><g clip-path="url(#@@{uid}h)">{nest(HIND, 104, 106, (.8, .6))}</g>'
        out += stroke("M98 108C84 102 66 98 50 98", "mband", 2.6) + f'<path d="M60 106L69 103L67 112Z" {F("mwin")}/>'
    out += f'<path d="{HIND}" fill="none" {S("medge")} stroke-width="2" stroke-linejoin="round"/>'
    # body
    out += f'<path d="{BODY}" {F("mbody")}/>'
    if detail:
        out += "".join(stroke(f"M{x} {y}l{4} {9}", "mwing", 1.2, 'opacity=".6"') for x, y in [(72, 112), (80, 107), (88, 103), (96, 100)])
    out += f'<ellipse cx="114" cy="103" rx="13" ry="10.5" {F("mbody")}/><circle cx="129" cy="98" r="6.6" {F("mbody")}/>'
    out += stroke("M108 112l-5 9M115 113l0 9M122 110l6 7", "mbody", 2)
    # near forewing
    out += f'<path d="{FORE}" {F("mwing")}/>'
    if detail:
        out += f'<clipPath id="@@{uid}f"><path d="{FORE}"/></clipPath><g clip-path="url(#@@{uid}f)">{nest(FORE, 108, 100, (.8, .62, .44))}</g>'
        out += stroke("M110 48C98 60 86 72 72 82", "mband", 3)
        out += f'<path d="M86 58L97 53L95 66Z" {F("mwin")} {S("medge")} stroke-width="1"/>'
    out += f'<path d="{HOOK}" {F("mhook")} {S("medge")} stroke-width="1.4" stroke-linejoin="round"/>'
    out += f'<path d="{FORE}" fill="none" {S("medge")} stroke-width="2.2" stroke-linejoin="round"/>'
    # feathered antennae, swept forward
    out += antenna("M132 93C140 82 150 76 162 75", [(135 + i*3.8, 89 - i*2.2 + i*i*.08) for i in range(7)])
    out += antenna("M130 92C135 80 142 72 152 68", [(132 + i*2.9, 87.5 - i*3 + i*i*.1) for i in range(7)])
    return out

def side_moth_icon():
    return (f'<path d="{FAR_FORE}" {F("mwing2")}/><path d="{FAR_HOOK}" {F("mwing2")}/><path d="{HIND}" {F("mwing2")}/><path d="{HOOK}" {F("mwing")}/><path d="{BODY}" {F("mbody")}/>'
            f'<ellipse cx="114" cy="103" rx="13" ry="10.5" {F("mbody")}/><circle cx="129" cy="98" r="7" {F("mbody")}/><path d="{FORE}" {F("mwing")}/>'
            + stroke("M132 93C140 82 150 76 162 75", "mbody", 4))

def place(body, x, y, s, rot=0):
    """Moth local centre is (90, 72)."""
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot}) scale({s}) translate(-90 -72)">{body}</g>'

def glow(cx, cy, r_in, r_a, r_b, n=36, w=1.2, c="acc"):
    return "".join(stroke(f"M{cx + r_in*math.cos(math.radians(a)):.1f} {cy + r_in*math.sin(math.radians(a)):.1f}L{cx + (r_a if i % 2 else r_b)*math.cos(math.radians(a)):.1f} {cy + (r_a if i % 2 else r_b)*math.sin(math.radians(a)):.1f}", c, w) for i, a in enumerate(range(0, 360, 360//n)))

def trail(d, w=1.8):
    return stroke(d, "acc", w, 'stroke-dasharray="0.1 5.5"')

V = []
def variant(name, idea, full, small):
    V.append(dict(n=len(V)+1, name=name, idea=idea, full=merge(full), small=merge(small)))

# 1 Lead: moth crossing in front of the lower left of the glowing globe
g1 = Globe(cx=112, cy=92, r=62, tilt=26, lon0=-22)
gi = Globe(cx=114, cy=92, r=74, tilt=26, lon0=-22)
variant("Into the Light",
        "The Pole A globe glows like a lamp, and the atlas moth flies past it in profile, crossing in front of the globe toward the light. A dotted trail shows where it has come from.",
        glow(112, 92, 68, 86, 78) + sphere(g1) + letters(g1, L=LIMB_L, w=7.5) +
        trail("M4 186C24 176 30 150 54 150") + place(side_moth("a"), 66, 140, .62, -12),
        sphere(gi, "solid", 30, 30) + letters(gi, L=LIMB_L, w=13) + place(side_moth("ai", detail=False), 60, 150, .66, -12))

# 2 The moth large, the globe behind it as the light source
g2 = Globe(cx=124, cy=82, r=52, tilt=26, lon0=-22)
variant("Moth First",
        "The moth is the hero and the globe is the light behind it. The moth's wings overlap the globe's lower edge, so the two read as one shape.",
        glow(124, 82, 58, 76, 68, 40, 1) + sphere(g2) + letters(g2, L=LIMB_L, w=6.5) +
        trail("M2 160C20 168 26 140 44 138") + place(side_moth("b"), 86, 130, .95, -10),
        sphere(Globe(cx=128, cy=76, r=60, tilt=26, lon0=-22), "solid", 30, 30) + letters(Globe(cx=128, cy=76, r=60, tilt=26, lon0=-22), L=LIMB_L, w=11) +
        place(side_moth("bi", detail=False), 82, 138, 1.05, -10))

# 3 Silhouette: the moth as a dark shape crossing the lit globe, like a bird across the moon
g3 = Globe(cx=100, cy=100, r=74, tilt=26, lon0=-22)
def silhouette():
    return f'<g {F("ground")}><path d="{FAR_FORE}"/><path d="{FAR_HOOK}"/><path d="{HOOK}"/><path d="{HIND}"/><path d="{BODY}"/><ellipse cx="114" cy="103" rx="13" ry="10.5"/><circle cx="129" cy="98" r="6.6"/><path d="{FORE}"/></g>' + \
           stroke("M132 93C140 82 150 76 162 75M130 92C135 80 142 72 152 68", "ground", 2.2)
variant("Silhouette",
        "The moth as a single dark shape crossing the lit globe, like a bird across a full moon. It's the boldest and simplest version, and the best one for stamping, embroidery and one-colour print.",
        glow(100, 100, 80, 96, 88, 48, 1) + f'<circle cx="100" cy="100" r="74" {F("acc")}/>' +
        stroke(g3.graticule(15, 15), "shade", .8, 'opacity=".55"') + stroke(letters(g3, L=LIMB_L, w=8).split('d="')[1].split('"')[0], "ground", 8, 'opacity=".22"') +
        place(silhouette(), 84, 118, .78, -14),
        f'<circle cx="100" cy="100" r="88" {F("acc")}/>' + place(silhouette(), 84, 122, .95, -14))

# 4 Plain globe, no letters, for comparison
g4 = Globe(cx=112, cy=92, r=62, tilt=26, lon0=-22)
variant("Plain Globe",
        "The same scene with no letters anywhere, so the globe and the moth carry the whole identity. Shown in case you'd rather keep Lab Atlas as a wordmark beside the symbol.",
        glow(112, 92, 68, 86, 78) + sphere(g4) + f'<circle cx="{g4.xy(90, 0)[0]:.2f}" cy="{g4.xy(90, 0)[1]:.2f}" r="3.4" {F("acc")}/>' +
        trail("M4 186C24 176 30 150 54 150") + place(side_moth("d"), 66, 140, .62, -12),
        sphere(gi, "solid", 20, 20) + place(side_moth("di", detail=False), 60, 150, .66, -12))

# 5 Seal: the scene inside a graduated ring
g5 = Globe(cx=106, cy=94, r=50, tilt=26, lon0=-22)
variant("Night Seal",
        "The scene set inside a graduated bezel with stars, as a seal for print, stickers and merchandise. The moth breaks out over the ring on the left.",
        PA.bezel() + glow(106, 94, 55, 70, 63, 36, .9) + sphere(g5) + letters(g5, L=LIMB_L, w=6.5) +
        "".join(f'<circle cx="{x}" cy="{y}" r="{r}" {F("acc")}/>' for x, y, r in [(50, 46, 1.4), (160, 150, 1.2), (60, 156, 1), (150, 36, 1)]) +
        place(side_moth("e"), 52, 136, .58, -12),
        f'<circle cx="100" cy="100" r="94" fill="none" {S("ring")} stroke-width="8"/>' + sphere(Globe(cx=108, cy=92, r=62, tilt=26, lon0=-22), "solid", 30, 30) +
        letters(Globe(cx=108, cy=92, r=62, tilt=26, lon0=-22), L=LIMB_L, w=11) + place(side_moth("ei", detail=False), 56, 146, .66, -12))

# 6 Orbit: the moth circling the globe on a dotted orbit, passing in front
g6 = Globe(cx=100, cy=96, r=58, tilt=26, lon0=-22)
orbit_back = f'<ellipse cx="100" cy="104" rx="90" ry="26" transform="rotate(-14 100 104)" fill="none" {S("acc")} stroke-width="1.6" stroke-dasharray="0.1 5" opacity=".6"/>'
orbit_front = f'<path d="M12.7 126.6A90 26 -14 0 0 187.3 81.4" transform="rotate(0)" fill="none" {S("acc")} stroke-width="1.8" stroke-dasharray="0.1 5"/>'
variant("Orbit",
        "The moth circles the glowing globe on a dotted orbit, like a moon. It passes in front of the globe at the low point of its path.",
        glow(100, 96, 64, 82, 74, 36, 1) + orbit_back + sphere(g6) + letters(g6, L=LIMB_L, w=7) + orbit_front + place(side_moth("f"), 120, 142, .5, -18),
        sphere(Globe(cx=100, cy=92, r=70, tilt=26, lon0=-22), "solid", 30, 30) + letters(Globe(cx=100, cy=92, r=70, tilt=26, lon0=-22), L=LIMB_L, w=12) +
        place(side_moth("fi", detail=False), 116, 156, .62, -18))

# ---------------------------------------------------------------- page
def svg(body, size, key): return f'<svg viewBox="0 0 200 200" width="{size}" height="{size}" aria-hidden="true">{body.replace("@@", f"d{key}-")}</svg>'

def export():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for k, p in PAL.items():
        for v in V:
            for kind in ("full", "small"):
                body = v[kind].replace("@@", "d")
                body = re.sub(r'style="([^"]*)"', lambda m: " ".join(f'{a}="{p[b]}"' for a, b in re.findall(r'(fill|stroke):var\(--(\w+)\)', m.group(1))), body)
                body = re.sub(r'<g fill="([^"]+)"><path', r'<g fill="\1"><path', body)
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
    solo = "".join(f'<div class="tile" style="{tokens(p)}">{svg(place(side_moth(f"s{k}", halo=False), 100, 100, 1.1), 200, f"so{k}")}</div>' for k, p in PAL.items())
    body = f'''<div class="wrap">
  <p class="eyebrow">Lab Atlas · round five</p>
  <h1>Drawn to the light</h1>
  <p class="lede">Moths are drawn to light, and students are drawn to research. The Pole A globe is the light, and the atlas moth now flies past it in profile: no face, and no letters on its wings. Its forewing still ends in the hooked, snake-head tip of the real atlas moth.</p>
  {hero}
  <h2>Six compositions</h2>
  <p class="sub">Each card shows the navy-and-gold and the earth palette, and the simplified version at 32 and 16 pixels.</p>
  <main class="plates">{plates}</main>
  <h2>The moth in profile</h2>
  <p class="sub">The side-view drawing used throughout: near and far forewings, a hindwing with its window, a segmented body and feathered antennae swept forward.</p>
  <div class="plates"><article class="plate"><div class="pair">{solo}</div></article></div>
</div>'''
    head = ('<title>Lab Atlas Light</title>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap">\n'
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
