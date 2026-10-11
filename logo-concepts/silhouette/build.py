"""Silhouette round: the side-view atlas moth as a dark shape crossing a lit globe,
framed by compass markings.

Usage: python3 build.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("light", os.path.join(HERE, "..", "drawn-to-the-light", "build.py"))
DL = importlib.util.module_from_spec(spec); spec.loader.exec_module(DL)
PA = DL.PA
from globe import Globe
F, S, stroke, merge, letters, LIMB_L = DL.F, DL.S, DL.stroke, DL.merge, DL.letters, DL.LIMB_L

# sil: the moth's colour; lit: the globe disc
PAL = {k: dict(DL.PAL[k]) for k in DL.PAL}
PAL["navy"].update(sil="#031b36", lit="#d4a72c", litline="#8c6d1f")
PAL["earth"].update(sil="#2e2419", lit="#c08a32", litline="#7d5a1c")
tokens = DL.tokens

# A falcate forewing: the outer margin curves in just below the apex, like the real atlas moth's tip.
FORE = "M121 95C122 70 112 42 97 17C93 22 90 27 86 30C76 44 64 54 54 64C70 82 86 96 97 104Z"
FAR_FORE = DL.turn(FORE, 13, -2, 9, 121, 95)

def moth_shape(c="sil", edge=None):
    parts = (f'<path d="{FAR_FORE}"/><path d="{DL.HIND}"/><path d="{DL.BODY}"/>'
             f'<ellipse cx="114" cy="103" rx="13" ry="10.5"/><circle cx="129" cy="98" r="6.6"/><path d="{FORE}"/>')
    out = ""
    if edge:
        out += f'<g {F(edge)} {S(edge)} stroke-width="5" stroke-linejoin="round">{parts}</g>' + stroke("M132 93C140 82 150 76 162 75M130 92C135 80 142 72 152 68M108 112l-5 9M115 113l0 9M122 110l6 7", edge, 5)
    out += f'<g {F(c)}>{parts}</g>'
    out += stroke("M132 93C140 82 150 76 162 75M130 92C135 80 142 72 152 68", c, 2.2)
    out += stroke("M108 112l-5 9M115 113l0 9M122 110l6 7", c, 2)
    return out

def place(body, x, y, s, rot=0): return DL.place(body, x, y, s, rot)

def pt(a, r, cx=100, cy=100):
    return cx + r*math.cos(math.radians(a)), cy + r*math.sin(math.radians(a))

def compass(r_in=69, c="ring", major=True, rose=False, w=1):
    """Graduated compass ring: fine ticks every 5 degrees, longer every 15 and 45, and
    half-shaded pointers at the four cardinal points. North is longest and carries a star."""
    out = f'<circle cx="100" cy="100" r="{r_in}" fill="none" {S(c)} stroke-width="{1.4*w}"/>'
    d = ""
    for i in range(72):
        a = i*5; L = 10 if a % 45 == 0 else (7 if a % 15 == 0 else 4)
        if a % 90 == 0: continue
        (x1, y1), (x2, y2) = pt(a, r_in + 1.5), pt(a, r_in + 1.5 + L)
        d += f"M{x1:.2f} {y1:.2f}L{x2:.2f} {y2:.2f}"
    out += stroke(d, c, .9*w)
    out += f'<circle cx="100" cy="100" r="{r_in + 15}" fill="none" {S(c)} stroke-width="{.8*w}"/>'
    if major:
        for a in (-90, 0, 90, 180):
            L = 30 if a == -90 else 22
            tip = pt(a, r_in + L); l = pt(a - 6, r_in + 1); r = pt(a + 6, r_in + 1)
            out += f'<path d="M{l[0]:.2f} {l[1]:.2f}L{tip[0]:.2f} {tip[1]:.2f}L{pt(a, r_in+4)[0]:.2f} {pt(a, r_in+4)[1]:.2f}Z" {F(c)}/>'
            out += f'<path d="M{r[0]:.2f} {r[1]:.2f}L{tip[0]:.2f} {tip[1]:.2f}L{pt(a, r_in+4)[0]:.2f} {pt(a, r_in+4)[1]:.2f}Z" {F("ground")} {S(c)} stroke-width="{.9*w}" stroke-linejoin="round"/>'
        for a in (-45, 45, 135, 225):
            tip = pt(a, r_in + 14); l = pt(a - 4, r_in + 1); r = pt(a + 4, r_in + 1)
            out += f'<path d="M{l[0]:.2f} {l[1]:.2f}L{tip[0]:.2f} {tip[1]:.2f}L{r[0]:.2f} {r[1]:.2f}Z" {F(c)}/>'
        out += PA.star(*pt(-90, r_in + 30 + 5), 4.2, "acc")
    return out

def rose_behind(r=88, c="ring"):
    """An eight-point compass rose behind the globe; only its points show past the disc."""
    out = ""
    for i in range(8):
        a = -90 + i*45; L = r if i % 2 == 0 else r*.72; W = 9 if i % 2 == 0 else 7
        tip = pt(a, L); l = pt(a - 90, W); rr = pt(a + 90, W)
        out += f'<path d="M100 100L{tip[0]:.2f} {tip[1]:.2f}L{l[0]:.2f} {l[1]:.2f}Z" {F(c)}/>'
        out += f'<path d="M100 100L{tip[0]:.2f} {tip[1]:.2f}L{rr[0]:.2f} {rr[1]:.2f}Z" {F("ground")} {S(c)} stroke-width=".9" stroke-linejoin="round"/>'
    return out

def lit_globe(r=62, la=True, grid=15, cx=100, cy=100):
    g = Globe(cx=cx, cy=cy, r=r, tilt=26, lon0=-22)
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" {F("lit")}/>'
    out += f'<clipPath id="@@g{r}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath><g clip-path="url(#@@g{r})">' + stroke(g.graticule(grid, grid), "litline", .9, 'opacity=".75"') + '</g>'
    if la:
        d = re.search(r'd="([^"]+)"', letters(g, L=LIMB_L)).group(1)
        out += stroke(d, "litline", r*.1) + stroke(g.parallel(15, -30, 30), "litline", r*.08)
    return out

V = []
def variant(name, idea, full, small):
    V.append(dict(n=len(V)+1, name=name, idea=idea, full=merge(full), small=merge(small)))

MOTH_AT = (98, 106, .64, -14)

variant("Compass Silhouette",
        "The lead version. The atlas moth crosses the lit globe as a single dark shape. Pole A is engraved faintly into the globe, and a graduated compass ring with half-shaded cardinal pointers replaces the rays of light. North carries a star.",
        compass() + lit_globe() + place(moth_shape(), *MOTH_AT),
        f'<circle cx="100" cy="100" r="95" fill="none" {S("ring")} stroke-width="6"/>' + lit_globe(80, la=False, grid=30) + place(moth_shape(), 100, 106, .8, -14))

variant("Plain Compass",
        "The same compass ring and moth with no letters on the globe, so the shapes carry everything and the name lives in the wordmark beside it.",
        compass() + lit_globe(la=False) + place(moth_shape(), *MOTH_AT),
        f'<circle cx="100" cy="100" r="95" fill="none" {S("ring")} stroke-width="6"/>' + lit_globe(80, la=False, grid=30) + place(moth_shape(), 100, 106, .8, -14))

variant("Rose Behind",
        "An eight-point compass rose sits behind the globe, so only its points show around the edge, like the globe has risen in front of a sea chart.",
        rose_behind() + f'<circle cx="100" cy="100" r="66" {F("ground")}/>' + lit_globe() + place(moth_shape(), *MOTH_AT),
        rose_behind(98) + f'<circle cx="100" cy="100" r="72" {F("ground")}/>' + lit_globe(68, la=False, grid=30) + place(moth_shape(), 100, 106, .74, -14))

variant("Breaking the Ring",
        "A plain graduated ring with no pointers. The moth's wings break out past it on the lower left, as if it is flying out of the compass.",
        compass(major=False) + lit_globe() + place(moth_shape(edge="lit"), 72, 128, .82, -14),
        f'<circle cx="100" cy="100" r="88" fill="none" {S("ring")} stroke-width="7"/>' + lit_globe(76, la=False, grid=30) + place(moth_shape(edge="lit"), 74, 132, .96, -14))

variant("One Colour",
        "Everything in a single ink: globe, compass and moth. It's built for a rubber stamp, embroidery, an etched glass, or any print where only one colour is possible.",
        compass(c="ring") + f'<circle cx="100" cy="100" r="62" {F("ring")}/>' +
        f'<clipPath id="@@o"><circle cx="100" cy="100" r="62"/></clipPath><g clip-path="url(#@@o)">' + stroke(Globe(r=62, tilt=26, lon0=-22).graticule(15, 15), "ground", .8, 'opacity=".35"') + '</g>' +
        place(moth_shape("ground"), *MOTH_AT),
        f'<circle cx="100" cy="100" r="95" fill="none" {S("ring")} stroke-width="6"/><circle cx="100" cy="100" r="80" {F("ring")}/>' + place(moth_shape("ground"), 100, 106, .8, -14))

variant("Night Globe",
        "The globe stays dark and the moth is gold, lit from behind. It's the reverse of the silhouette, for dark backgrounds, merchandise and the site's footer.",
        compass() + f'<circle cx="100" cy="100" r="62" {F("sea")}/>' +
        f'<clipPath id="@@n"><circle cx="100" cy="100" r="62"/></clipPath><g clip-path="url(#@@n)">' + stroke(Globe(r=62, tilt=26, lon0=-22).graticule(15, 15), "grid", .9) + '</g>' +
        f'<circle cx="100" cy="100" r="62" fill="none" {S("ring")} stroke-width="2.2"/>' + place(moth_shape("acc"), *MOTH_AT),
        f'<circle cx="100" cy="100" r="95" fill="none" {S("ring")} stroke-width="6"/><circle cx="100" cy="100" r="80" {F("sea")}/>' + place(moth_shape("acc"), 100, 106, .8, -14))

def svg(body, size, key): return f'<svg viewBox="0 0 200 200" width="{size}" height="{size}" aria-hidden="true">{body.replace("@@", f"s{key}-")}</svg>'

def export():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for k, p in PAL.items():
        for v in V:
            for kind in ("full", "small"):
                body = v[kind].replace("@@", "s")
                body = re.sub(r'style="([^"]*)"', lambda m: " ".join(f'{a}="{p[b]}"' for a, b in re.findall(r'(fill|stroke):var\(--(\w+)\)', m.group(1))), body)
                slug = re.sub(r"[^a-z0-9]+", "-", v["name"].lower()).strip("-")
                with open(os.path.join(out, f"{v['n']:02d}-{slug}-{k}{'' if kind=='full' else '-small'}.svg"), "w") as fh:
                    fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="400" height="400"><title>{html.escape(v["name"])}</title>'
                             f'<rect width="200" height="200" fill="{p["ground"]}"/><g transform="translate(6 6) scale(.94)">{body}</g></svg>\n')

def page(fonts, full_doc):
    nv, ea = tokens(PAL["navy"]), tokens(PAL["earth"])
    lead = V[0]
    hero = f'''<div class="hero">
  <div class="tile" style="{nv}">{svg(lead["full"], 520, "h1")}</div>
  <div class="hero-side">
    <div class="hero-pair"><div class="tile" style="{ea}">{svg(lead["full"], 240, "h2")}</div><div class="tile" style="{nv}">{svg(V[5]["full"], 240, "h3")}</div></div>
    <div><p class="cap">In use</p>
      <div class="nav" style="{nv}">{svg(lead["small"], 32, "n1")}<b>Lab Atlas</b><span>Find a lab</span></div>
      <div class="nav" style="{ea};margin-top:10px">{svg(lead["small"], 32, "n2")}<b>Lab Atlas</b><span>Find a lab</span></div></div>
    <div class="apps">
      <figure><span class="app" style="{nv};width:84px;height:84px;border-radius:20px">{svg(lead["small"], 70, "a1")}</span>App icon</figure>
      <figure><span class="app" style="{ea};width:84px;height:84px;border-radius:20px">{svg(lead["small"], 70, "a2")}</span>App icon</figure>
      <figure><span class="app" style="{nv};width:32px;height:32px;border-radius:7px">{svg(lead["small"], 30, "a3")}</span>32 px</figure>
      <figure><span class="app" style="{nv};width:16px;height:16px;border-radius:4px">{svg(lead["small"], 16, "a4")}</span>16 px</figure>
    </div>
  </div>
</div>'''
    plates = ""
    for v in V:
        tiles = "".join(f'<div class="tile" style="{tokens(p)}">{svg(v["full"], 200, f"{v["n"]}{k}")}</div>' for k, p in PAL.items())
        chips = "".join(f'<span class="chip c32" style="{tokens(p)}">{svg(v["small"], 30, f"{v["n"]}{k}s")}</span><span class="chip c16" style="{tokens(p)}">{svg(v["small"], 15, f"{v["n"]}{k}t")}</span>' for k, p in PAL.items())
        plates += f'''<article class="plate"><div class="pair">{tiles}</div><div class="meta">
  <div class="row"><span class="no">{v["n"]:02d}</span><h3>{html.escape(v["name"])}</h3></div>
  <p class="why">{html.escape(v["idea"])}</p><div class="small">Small{chips}</div></div></article>\n'''
    body = f'''<div class="wrap">
  <p class="eyebrow">Lab Atlas · round six</p>
  <h1>Silhouette in the compass</h1>
  <p class="lede">The atlas moth, in profile and without a face, crosses the lit globe as a single dark shape. The rays of light are gone; in their place is a navigator's compass ring with graduated ticks and half-shaded pointers at the four cardinal points.</p>
  {hero}
  <h2>Six versions</h2>
  <p class="sub">Each card shows the navy-and-gold and the earth palette, and the simplified version at 32 and 16 pixels.</p>
  <main class="plates">{plates}</main>
</div>'''
    head = ('<title>Lab Atlas Silhouette</title>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap">\n'
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
