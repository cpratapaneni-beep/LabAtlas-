"""Atlas round: the titan Atlas carrying the globe, as a black-figure silhouette inside a compass.

Usage: python3 build.py [atlas-text.css] [artifact-out.html]
"""
import math, os, re, sys, html, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("sil", os.path.join(HERE, "..", "silhouette", "build.py"))
SI = importlib.util.module_from_spec(spec); spec.loader.exec_module(SI)
PA = SI.PA
from globe import Globe
from figure import kneeling, standing, shoulders
F, S, stroke, merge, letters, LIMB_L, tokens = SI.F, SI.S, SI.stroke, SI.merge, SI.letters, SI.LIMB_L, SI.tokens
PAL = SI.PAL

def carried_globe(cx, cy, r, body="sil", line="lit", la=True, grid=15):
    """The sphere Atlas carries: a dark ball with its graticule incised in the light colour,
    as on a black-figure vase. Pole A can be incised into it too."""
    g = Globe(cx=cx, cy=cy, r=r, tilt=26, lon0=-22)
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" {F(body)}/>'
    out += f'<clipPath id="@@c{cx}{cy}"><circle cx="{cx}" cy="{cy}" r="{r - 1.2}"/></clipPath><g clip-path="url(#@@c{cx}{cy})">' + stroke(g.graticule(grid, grid), line, max(.7, r*.018), 'opacity=".75"') + '</g>'
    if la:
        d = re.search(r'd="([^"]+)"', letters(g, L=LIMB_L)).group(1)
        out += stroke(d, line, r*.085) + stroke(g.parallel(15, -30, 30), line, r*.07)
    return out

def group(body, s, dx, dy):
    return f'<g transform="translate({dx} {dy}) scale({s})">{body}</g>'

def scene_kneel(fig="sil", ball="sil", line="lit", la=True, s=.72, dx=36, dy=26):
    return group(carried_globe(96, 70, 44, ball, line, la) + kneeling(fig), s, dx, dy)

def scene_stand(fig="sil", ball="sil", line="lit", la=True, s=.74, dx=26, dy=22):
    return group(carried_globe(100, 64, 40, ball, line, la) + standing(fig), s, dx, dy)

def disc(r=67, c="lit"): return f'<circle cx="100" cy="100" r="{r}" {F(c)}/>'

def meander(r1=72, r2=86, n=28, c="ring", w=1.6):
    """A Greek key running around the ring between radius r1 and r2."""
    unit = [(0, 0), (0, 1), (.75, 1), (.75, .25), (.5, .25), (.5, .75), (.25, .75), (.25, 0), (1, 0)]
    pts = []
    for k in range(n):
        for (x0, y0), (x1, y1) in zip(unit, unit[1:]):
            steps = 6 if y0 == y1 else 1
            for t in range(steps + 1):
                x = k + x0 + (x1 - x0)*t/steps; y = y0 + (y1 - y0)*t/steps
                a = math.radians(-90 + 360*x/n); r = r1 + (r2 - r1)*y
                pts.append((100 + r*math.cos(a), 100 + r*math.sin(a)))
    d = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"
    return (f'<circle cx="100" cy="100" r="{r1 - 3}" fill="none" {S(c)} stroke-width="{w*.8}"/><circle cx="100" cy="100" r="{r2 + 3}" fill="none" {S(c)} stroke-width="{w*.8}"/>'
            + f'<path d="{d}" fill="none" {S(c)} stroke-width="{w}" stroke-linejoin="miter"/>')

V = []
def variant(name, idea, full, small):
    V.append(dict(n=len(V)+1, name=name, idea=idea, full=merge(full), small=merge(small)))

SMALL_RING = f'<circle cx="100" cy="100" r="95" fill="none" {S("ring")} stroke-width="6"/>'
def small_bust(bg="lit", fig="sil", line="lit"):
    return SMALL_RING + f'<clipPath id="@@sb"><circle cx="100" cy="100" r="86"/></clipPath>' + disc(86, bg) + \
           f'<g clip-path="url(#@@sb)">{group(carried_globe(100, 74, 56, fig, line, la=False, grid=30) + shoulders(fig), .86, 14, 18)}</g>'

variant("Farnese Atlas",
        "The titan in the pose of the Farnese Atlas, the best-known statue of him: one knee on the ground and his back bent under the heavens, steadying the sphere with both hands. He is a single dark figure on the lit disc, and the sphere he carries has the globe grid and Pole A cut into it. The compass ring frames the scene.",
        SI.compass() + disc() + scene_kneel(),
        small_bust())

variant("Standing Titan",
        "Atlas standing square with the sphere on his shoulders and his arms raised to hold it. His legs and the line across them form an A, so the figure spells half the name.",
        SI.compass() + disc() + scene_stand(),
        SMALL_RING + disc(86) + group(carried_globe(100, 64, 40, la=False, grid=30) + standing(s=1.3), 1.0, 0, 4))

variant("Black-figure Vase",
        "Drawn like a Greek black-figure vase: a dark figure on clay-coloured ground, details cut in as fine lines, and a Greek key running around the edge in place of the compass.",
        meander() + disc(66) + scene_kneel(),
        f'<circle cx="100" cy="100" r="95" fill="none" {S("ring")} stroke-width="4"/>' + meander(78, 94, 14, w=4) + disc(72) +
        group(carried_globe(100, 74, 56, la=False, grid=30) + shoulders(), .74, 26, 26))

variant("Titan's Shoulders",
        "A close-up of the bowed head, shoulders and raised arms under the sphere. It's the most compact version, made for favicons, avatars and app icons where the whole figure would be too small.",
        SI.compass() + f'<clipPath id="@@ts"><circle cx="100" cy="100" r="67"/></clipPath>' + disc() +
        f'<g clip-path="url(#@@ts)">{group(carried_globe(100, 74, 56) + shoulders(), .7, 30, 30)}</g>',
        small_bust())

variant("Night Titan",
        "The reverse version for dark grounds: a dark sky disc with a gold titan and a gold sphere whose lines are cut in dark.",
        SI.compass() + disc(c="sea") + f'<circle cx="100" cy="100" r="67" fill="none" {S("ring")} stroke-width="2"/>' + scene_kneel("acc", "acc", "sea"),
        small_bust("sea", "acc", "sea"))

variant("One Colour",
        "The titan, the sphere and the compass in a single ink, for stamps, embroidery, engraving on glass or metal, and one-colour print.",
        SI.compass() + disc(c="ring") + scene_kneel("ground", "ground", "ring"),
        small_bust("ring", "ground", "ring"))

def svg(body, size, key): return f'<svg viewBox="0 0 200 200" width="{size}" height="{size}" aria-hidden="true">{body.replace("@@", f"t{key}-")}</svg>'

def export():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for k, p in PAL.items():
        for v in V:
            for kind in ("full", "small"):
                body = v[kind].replace("@@", "t")
                body = re.sub(r'style="([^"]*)"', lambda m: " ".join(f'{a}="{p[b]}"' for a, b in re.findall(r'(fill|stroke):var\(--(\w+)\)', m.group(1))), body)
                slug = re.sub(r"[^a-z0-9]+", "-", v["name"].lower()).strip("-")
                with open(os.path.join(out, f"{v['n']:02d}-{slug}-{k}{'' if kind=='full' else '-small'}.svg"), "w") as fh:
                    fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="400" height="400"><title>{html.escape(v["name"])}</title>'
                             f'<rect width="200" height="200" fill="{p["ground"]}"/><g transform="translate(6 6) scale(.94)">{body}</g></svg>\n')

def page(fonts, full_doc):
    html_ = SI.page(fonts, full_doc)
    return html_

if __name__ == "__main__":
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    SI.V[:] = V
    SI.svg = svg
    export()
    def fix(t):
        t = t.replace("<title>Lab Atlas Silhouette</title>", "<title>Lab Atlas Titan</title>")
        t = t.replace("Lab Atlas · round six", "Lab Atlas · round seven")
        t = t.replace("<h1>Silhouette in the compass</h1>", "<h1>Atlas, bearing the heavens</h1>")
        t = re.sub(r'<p class="lede">.*?</p>', '<p class="lede">In Greek myth the titan Atlas was condemned to hold up the heavens forever, and his image on the title pages of early map books is why we call them atlases. Here he carries the Pole A globe as a black-figure silhouette on a lit disc, inside the navigator\'s compass ring. The moth is gone.</p>', t, flags=re.S)
        return t
    open(os.path.join(HERE, "index.html"), "w").write(fix(SI.page(fonts, True)))
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(fix(SI.page(fonts, False)))
    print("built", len(V))
