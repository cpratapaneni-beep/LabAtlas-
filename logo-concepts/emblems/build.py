"""Lab Atlas emblems: round two, in an engraved-atlas and seal style.

Usage: python3 build.py [path/to/atlas-text.css] [artifact-out.html]

Each emblem is drawn on a 200x200 grid with hatching, stipple, bezels and
laurels, in the manner of an old atlas plate. Each one also has a `core`:
a reduced version for favicons and app icons, where fine engraving can't
survive. Colours are CSS variables, so every emblem renders in both palettes.
"""
import math, os, re, sys, html, random

HERE = os.path.dirname(os.path.abspath(__file__))

PALETTES = {
    "navy":  {"name": "Navy & gold", "ground": "#031b36", "ink": "#d4a72c", "a1": "#fdffee", "a2": "#8c6d1f", "a3": "#e9cf86"},
    "earth": {"name": "Earth",       "ground": "#f1e7d0", "ink": "#2e2419", "a1": "#b07d2a", "a2": "#7f8a62", "a3": "#8e4f2f"},
}
CX = CY = 100

# ------------------------------------------------------------- primitives
def fill(c): return f'style="fill:var(--{c})"'
def strk(c): return f'style="stroke:var(--{c})"'

def path(d, c="ink", w=1.5, fill_c=None, extra=""):
    f = fill(fill_c) if fill_c else 'fill="none"'
    if fill_c and c is None:
        return f'<path d="{d}" {f} {extra}/>'
    return f'<path d="{d}" {f} {strk(c)} stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'

def circ(r, c="ink", w=1.5, cx=CX, cy=CY, fill_c=None, extra=""):
    f = fill(fill_c) if fill_c else 'fill="none"'
    s = f'{strk(c)} stroke-width="{w}"' if c else ""
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" {f} {s} {extra}/>'

def dot(x, y, r, c="ink", extra=""):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" {fill(c)} {extra}/>'

def pt(a, r, cx=CX, cy=CY):
    a = math.radians(a)
    return cx + r*math.cos(a), cy + r*math.sin(a)

def poly(pts, c="ink", extra=""):
    return f'<path d="M{" L".join(f"{x:.2f} {y:.2f}" for x, y in pts)}Z" {fill(c)} {extra}/>'

def star(x, y, R, c="a1", n=5, ratio=.42, rot=-90):
    pts = []
    for i in range(n*2):
        r = R if i % 2 == 0 else R*ratio
        a = math.radians(rot + i*180/n)
        pts.append((x + r*math.cos(a), y + r*math.sin(a)))
    return poly(pts, c)

def sparkle(x, y, R, c="a1"):
    return star(x, y, R, c, n=4, ratio=.22)

def ticks(r_in, short, long, n, every, c="ink", w=1, cx=CX, cy=CY):
    d = ""
    for i in range(n):
        a = i*360/n
        L = long if i % every == 0 else short
        x1, y1 = pt(a, r_in, cx, cy); x2, y2 = pt(a, r_in+L, cx, cy)
        d += f"M{x1:.2f} {y1:.2f}L{x2:.2f} {y2:.2f}"
    return path(d, c, w)

def beads(r, n, size, c="ink", cx=CX, cy=CY):
    return "".join(dot(*pt(i*360/n, r, cx, cy), size, c) for i in range(n))

def star_ring(r, n, size, c="a1", skip=()):
    out = ""
    for i in range(n):
        if i in skip: continue
        x, y = pt(-90 + i*360/n, r)
        out += star(x, y, size, c)
    return out

def rays(r1, r2a, r2b, n, c="ink", w=1, cx=CX, cy=CY, a0=0, a1=360):
    d = ""
    for i in range(n):
        a = a0 + (a1-a0)*i/n
        x1, y1 = pt(a, r1, cx, cy); x2, y2 = pt(a, r2a if i % 2 == 0 else r2b, cx, cy)
        d += f"M{x1:.2f} {y1:.2f}L{x2:.2f} {y2:.2f}"
    return path(d, c, w)

def laurel(R, a_from, a_to, n, c="ink", size=(8, 3.2), cx=CX, cy=CY):
    """A branch along a circle from a_from to a_to (degrees, SVG orientation)."""
    x0, y0 = pt(a_from, R, cx, cy); x1, y1 = pt(a_to, R, cx, cy)
    sweep = 1 if a_to > a_from else 0
    large = 1 if abs(a_to-a_from) > 180 else 0
    out = path(f"M{x0:.2f} {y0:.2f}A{R} {R} 0 {large} {sweep} {x1:.2f} {y1:.2f}", c, 1.4)
    for i in range(n):
        t = (i + .5)/n
        a = a_from + (a_to-a_from)*t
        lx, ly = pt(a, R, cx, cy)
        grow = a + (90 if sweep else -90)
        L = size[0]*(1.05 - 0.3*t)
        for side in (-1, 1):
            d = grow + side*34
            px, py = lx + L*.95*math.cos(math.radians(d)), ly + L*.95*math.sin(math.radians(d))
            out += f'<ellipse cx="{px:.2f}" cy="{py:.2f}" rx="{L:.2f}" ry="{size[1]:.2f}" transform="rotate({d:.1f} {px:.2f} {py:.2f})" {fill(c)}/>'
    tx, ty = pt(a_to, R, cx, cy)
    g = a_to + (90 if sweep else -90)
    px, py = tx + size[0]*.6*math.cos(math.radians(g)), ty + size[0]*.6*math.sin(math.radians(g))
    out += f'<ellipse cx="{px:.2f}" cy="{py:.2f}" rx="{size[0]*.7:.2f}" ry="{size[1]*.9:.2f}" transform="rotate({g:.1f} {px:.2f} {py:.2f})" {fill(c)}/>'
    return out

def wreath(R=74, gap_top=30, n=9, c="ink", cy=CY):
    left = laurel(R, 96, 270-gap_top, n, c, cy=cy)
    right = laurel(R, 84, -90+gap_top, n, c, cy=cy)
    bx, by = pt(90, R, CX, cy)
    knot = (f'<path d="M{bx-6:.1f} {by+1:.1f}Q{bx:.1f} {by-6:.1f} {bx+6:.1f} {by+1:.1f}Q{bx:.1f} {by+8:.1f} {bx-6:.1f} {by+1:.1f}Z" {fill(c)}/>'
            + path(f"M{bx-3:.1f} {by+3:.1f}L{bx-8:.1f} {by+12:.1f}M{bx+3:.1f} {by+3:.1f}L{bx+8:.1f} {by+12:.1f}", c, 2))
    return left + right + knot

def hatch_lines(ang, gap, w, c, cx=CX, cy=CY, span=320):
    d = "".join(f"M{cx-span/2:.1f} {cy-span/2+k:.1f}H{cx+span/2:.1f}" for k in [i*gap for i in range(int(span/gap)+1)])
    return f'<g transform="rotate({ang} {cx} {cy})">{path(d, c, w)}</g>'

_uid = [0]
def uid():
    _uid[0] += 1
    return f"@@{_uid[0]}"

def clip(shape, body):
    i = uid()
    return f'<clipPath id="{i}">{shape}</clipPath><g clip-path="url(#{i})">{body}</g>'

def masked(mask_body, body):
    i = uid()
    return f'<mask id="{i}" maskUnits="userSpaceOnUse" x="0" y="0" width="200" height="200">{mask_body}</mask><g mask="url(#{i})">{body}</g>'

def shaded(mask_body, ang=45, gap=2.6, w=.8, c="ink"):
    return masked(mask_body, hatch_lines(ang, gap, w, c))

def crescent(cx, cy, r, dx=-.3, dy=-.3):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff"/>'
            f'<circle cx="{cx+dx*r:.2f}" cy="{cy+dy*r:.2f}" r="{r*1.04:.2f}" fill="#000"/>')

def globe(cx, cy, r, c="ink", lw=1.2, tilt=0, shade=True, shade_c="ink", outline=2.4, lat=(-60, -30, 0, 30, 60), mer=(30, 60)):
    g = ""
    inner = ""
    for k in mer:
        rx = r*math.sin(math.radians(k))
        inner += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.2f}" ry="{r}" fill="none" {strk(c)} stroke-width="{lw}"/>'
    inner += path(f"M{cx} {cy-r}V{cy+r}", c, lw)
    for la in lat:
        y = cy + r*math.sin(math.radians(la)); hw = r*math.cos(math.radians(la))
        bow = r*.13*math.cos(math.radians(la))
        inner += path(f"M{cx-hw-2:.2f} {y:.2f}Q{cx} {y+bow*2:.2f} {cx+hw+2:.2f} {y:.2f}", c, lw)
    g += clip(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>', f'<g transform="rotate({tilt} {cx} {cy})">{inner}</g>')
    if shade:
        g += shaded(crescent(cx, cy, r), 45, 2.4, .75, shade_c)
    g += circ(r, c, outline, cx, cy)
    return g

def blob(cx, cy, R, amp, seed, n=160):
    rnd = random.Random(seed)
    k = [(rnd.uniform(.3, 1), rnd.randint(2, 7), rnd.uniform(0, 6.3)) for _ in range(5)]
    def rad(t): return R*(1 + amp*sum(a*math.sin(f*t + p) for a, f, p in k)/3)
    pts = [(cx + rad(t)*math.cos(t), cy + rad(t)*math.sin(t)) for t in [2*math.pi*i/n for i in range(n)]]
    d = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"
    return d, rad

def stipple(cx, cy, rad, n, size, c, seed, inside_frac=1.0):
    rnd = random.Random(seed); out = ""
    for _ in range(n):
        t = rnd.uniform(0, 2*math.pi); u = math.sqrt(rnd.random())*inside_frac
        r = rad(t)*u
        out += dot(cx + r*math.cos(t), cy + r*math.sin(t), size*rnd.uniform(.6, 1.2), c)
    return out

def bezel(r_out=92, c="ink"):
    return circ(r_out, c, 1) + ticks(r_out-10, 4, 8, 72, 6, c, .9) + circ(r_out-10, c, 2.2)

def rflask(cx, cy, r, neck_w, neck_top, c="ink", w=3):
    hw = neck_w/2
    yj = cy - math.sqrt(r*r - hw*hw)
    return f"M{cx-hw:.2f} {neck_top}V{yj:.2f}A{r} {r} 0 1 0 {cx+hw:.2f} {yj:.2f}V{neck_top}"

def erlen(cx, top, neck_w, neck_h, base_y, base_w):
    hw, bw = neck_w/2, base_w/2
    return (f"M{cx-hw} {top}V{top+neck_h}L{cx-bw+4} {base_y-6}Q{cx-bw} {base_y} {cx-bw+7} {base_y}"
            f"H{cx+bw-7}Q{cx+bw} {base_y} {cx+bw-4} {base_y-6}L{cx+hw} {top+neck_h}V{top}")

def shield_d(x0=40, x1=160, y0=28, mid=98, tip=178):
    return f"M{x0} {y0}H{x1}V{mid}C{x1} {mid+42} {x1-28} {tip-16} 100 {tip}C{x0+28} {tip-16} {x0} {mid+42} {x0} {mid}Z"

def la_ligature(c="ink", dx=0, dy=0, s=1):
    shapes = [
        [(44, 60), (72, 60), (72, 64.5), (64, 64.5), (64, 132), (110, 132), (110, 118), (113, 118), (113, 137), (44, 137), (44, 132.5), (52, 132.5), (52, 64.5), (44, 64.5)],
        [(118.5, 58), (121.5, 58), (91.5, 133), (88.5, 133)],
        [(117, 58), (125, 58), (157, 132.5), (166, 132.5), (166, 137), (136, 137), (136, 132.5), (143, 132.5)],
        [(99.2, 108), (136.0, 108), (137.5, 111.5), (97.8, 111.5)],
    ]
    return f'<g transform="translate({dx} {dy}) scale({s})">' + "".join(poly(p, c) for p in shapes) + "</g>"

# ------------------------------------------------------------- emblems
E = []
_dup = re.compile(r'<([a-zA-Z]+)([^<>]*?)\sstyle="([^"]*)"([^<>]*?)\sstyle="([^"]*)"')
def merge_styles(body):
    """Elements that set both fill and stroke would otherwise carry two style attributes."""
    while True:
        new = _dup.sub(lambda m: f'<{m.group(1)}{m.group(2)} style="{m.group(3)};{m.group(5)}"{m.group(4)}', body)
        if new == body: return body
        body = new

def emblem(name, method, why, full, core):
    E.append(dict(n=len(E)+1, name=name, method=method, why=why, full=merge_styles(full), core=merge_styles(core)))

# 1 Armillary Flask
ff = rflask(100, 114, 36, 18, 54)
liquid = clip(f'<circle cx="100" cy="114" r="34"/>', hatch_lines(0, 2.6, .9, "ink") + path("M60 120Q100 130 140 120", "ink", 1.6))
liquid = masked('<rect width="200" height="200" fill="#000"/><path d="M60 120Q100 130 140 120V170H60Z" fill="#fff"/>', liquid)
rings = (f'<ellipse cx="100" cy="114" rx="58" ry="15" transform="rotate(-22 100 114)" fill="none" {strk("a1")} stroke-width="2"/>'
         f'<ellipse cx="100" cy="114" rx="58" ry="15" transform="rotate(22 100 114)" fill="none" {strk("a1")} stroke-width="2"/>'
         f'<ellipse cx="100" cy="114" rx="54" ry="6" fill="none" {strk("a1")} stroke-width="1.2" stroke-dasharray="1.2 2.4"/>')
emblem("Armillary Flask", "Engraved instrument",
       "A round-bottom flask set inside the rings of an armillary sphere, the old astronomer's model of the heavens. Lab glass and atlas instrument in one object.",
       bezel() + rays(84, 80, 77, 72, "a2", .6) + sparkle(100, 32, 7, "a1") + dot(100, 114, 1) + liquid +
       path(ff, "ink", 3) + path("M88 54H112", "ink", 3) + rings + dot(*pt(-22+180, 58, 100, 114), 2.6, "a1") + dot(*pt(-22, 58, 100, 114), 2.6, "a1"),
       f'<circle cx="100" cy="100" r="92" {fill("ground")}/>' + path(rflask(100, 112, 40, 22, 46), "ink", 9) + path("M84 46H116", "ink", 9) +
       f'<ellipse cx="100" cy="112" rx="70" ry="18" transform="rotate(-22 100 112)" fill="none" {strk("a1")} stroke-width="7"/>')

# 2 Portolan Rose
def rose(cx, cy, specs, north_c="a1", w=.8):
    out = ""
    for count, L, W, rot in specs:
        for i in range(count):
            a = rot + i*360/count
            tip = pt(a, L, cx, cy); l = pt(a-90, W, cx, cy); r = pt(a+90, W, cx, cy)
            first = (i == 0 and L == specs[0][1])
            out += poly([(cx, cy), tip, l], north_c if first else "ink")
            out += poly([(cx, cy), tip, r], "ground", f'{strk("ink")} stroke-width="{w}" stroke-linejoin="round"')
    return out
rh = "".join(path(f"M100 100L{pt(i*360/32, 84)[0]:.2f} {pt(i*360/32, 84)[1]:.2f}", "a2", .6) for i in range(32))
emblem("Portolan Rose", "Cartographic ornament",
       "A sixteen-point compass rose with the rhumb lines of a medieval sea chart. Each point is half-shaded the way engravers did it, and north is picked out in a lighter colour.",
       circ(92, "ink", 1) + beads(88, 72, 1.1) + circ(84, "ink", 2) + rh +
       rose(100, 100, [(4, 74, 11, -90), (4, 52, 9, -45), (8, 32, 5, -67.5)]) +
       circ(9, "ink", 1.4, fill_c="ground") + dot(100, 100, 3.4, "a1"),
       rose(100, 100, [(4, 90, 22, -90), (4, 54, 15, -45)], w=3) + dot(100, 100, 8, "a1"))

# 3 Globe Seal
emblem("Globe Seal", "Seal",
       "An engraved globe with hatched shading, held in a laurel wreath under a ring of stars. The classic shape of an academic seal, without any words.",
       circ(92, "ink", 1.2) + star_ring(86, 24, 2.6, "a1") + circ(80, "ink", 2) + circ(76, "ink", .8) +
       wreath(64, 34, 8, "ink", cy=104) + globe(100, 92, 40) + sparkle(100, 38, 6, "a1"),
       f'<circle cx="100" cy="100" r="92" {fill("ground")}/>' + globe(100, 100, 66, lw=4, outline=9, lat=(-35, 0, 35), mer=(55,), shade=False) +
       masked(crescent(100, 100, 66), f'<rect width="200" height="200" {fill("ink")} opacity=".35"/>'))

# 4 Laurel Flask
ef = erlen(100, 44, 18, 30, 150, 78)
emblem("Laurel Flask", "Seal",
       "An Erlenmeyer flask between two laurel branches, under a single star. The liquid is cross-hatched like an engraving, and the side carries graduation marks.",
       wreath(76, 40, 9, "ink", cy=102) + star(100, 26, 9, "a1") +
       masked(f'<path d="{ef}Z" fill="#fff"/><rect x="0" y="0" width="200" height="112" fill="#000"/>', hatch_lines(35, 2.6, .9, "ink") + hatch_lines(-35, 2.6, .9, "ink")) +
       path("M75 112Q100 118 125 112", "ink", 1.6) +
       path("".join(f"M{78+ (150-y)*0.0:.1f} {y}h6" for y in range(0)), "ink", 1) +
       "".join(path(f"M{100-9-(y-74)*0.53:.1f} {y}h{7 if i%2==0 else 4}", "ink", 1.2) for i, y in enumerate(range(84, 146, 8))) +
       circ(3.2, "a1", 1.2, 102, 66) + circ(2.2, "a1", 1.1, 97, 56) + circ(4, "a1", 1.2, 110, 98) +
       path(ef, "ink", 3) + path("M86 44H114", "ink", 3),
       path(erlen(100, 26, 26, 34, 172, 120), "ink", 10) + path("M80 26H120", "ink", 10) +
       masked(f'<path d="{erlen(100, 26, 26, 34, 172, 120)}Z" fill="#fff"/><rect width="200" height="122" fill="#000"/>', f'<rect width="200" height="200" {fill("a1")}/>'))

# 5 LA Monogram Seal
emblem("LA Ligature Seal", "Monogram seal",
       "A high-contrast Roman L and A joined into one ligature: the L's foot runs on as the A's left serif. Set in a graduated bezel like an instrument dial.",
       bezel() + circ(76, "ink", .8) + la_ligature("ink", -5, 3) + star(100, 40, 4.5, "a1") + star(100, 162, 4.5, "a1") +
       sparkle(36, 100, 4, "a1") + sparkle(164, 100, 4, "a1"),
       f'<rect x="4" y="4" width="192" height="192" rx="40" {fill("ground")}/>' + la_ligature("ink", -38, -30, 1.38))

# 6 Atlas Sphere
tilt = 23
ax0 = pt(-90+tilt, 52, 100, 74); ax1 = pt(90+tilt, 52, 100, 74)
emblem("Globe on an A", "Engraved instrument",
       "A library globe whose stand is a capital A, so the letter is literally holding up the world, the way Atlas does. The axis is tilted 23 degrees, like Earth's.",
       globe(100, 74, 40, tilt=tilt) +
       f'<circle cx="100" cy="74" r="47" fill="none" {strk("a1")} stroke-width="3.2" stroke-dasharray="210 400" transform="rotate({tilt+90+75} 100 74)"/>' +
       path(f"M{ax0[0]:.1f} {ax0[1]:.1f}L{ax1[0]:.1f} {ax1[1]:.1f}", "a1", 1.4) +
       path("M100 121V130M100 130L62 180M100 130L138 180M74 164H126", "ink", 4.5) + dot(100, 130, 4, "a1") +
       path("M46 182H154", "ink", 1.6) + path("M56 186H144", "ink", .8) + sparkle(30, 30, 5, "a1") + sparkle(170, 44, 3.5, "a1"),
       globe(100, 64, 52, lw=4, outline=8, lat=(0,), mer=(60,), shade=False) + path("M100 120V132M100 132L50 190M100 132L150 190M66 170H134", "ink", 11))

# 7 Contour Shield
cont = ""
for i, R in enumerate(range(12, 100, 9)):
    d, _ = blob(100, 104, R, .12, 5)
    cont += path(d, "ink", 2 if i % 4 == 3 else .9)
chief = clip(f'<rect x="40" y="28" width="120" height="24"/>', hatch_lines(0, 2.4, .8, "ink"))
emblem("Contour Shield", "Heraldic crest",
       "A shield engraved with topographic contour lines. Every fourth line is heavier, as on survey maps. The band across the top holds three stars.",
       clip(f'<path d="{shield_d()}"/>', cont + dot(100, 104, 3, "a1")) + chief + path("M40 52H160", "ink", 1.6) +
       star(72, 40, 5, "a1") + star(100, 40, 5, "a1") + star(128, 40, 5, "a1") +
       path(shield_d(), "ink", 3) + path(shield_d(46, 154, 34, 98, 170), "ink", .8),
       clip(f'<path d="{shield_d(24, 176, 14, 96, 192)}"/>', "".join(path(blob(100, 108, R, .12, 5)[0], "ink", 7) for R in (24, 48, 72))) +
       path(shield_d(24, 176, 14, 96, 192), "ink", 10))

# 8 Helix Globe
def helix_pts(sign, r=60, n=80):
    pts = []
    for i in range(n+1):
        y = 100 - r + 2*r*i/n
        amp = .78*math.sqrt(max(r*r - (y-100)**2, 0))
        pts.append((100 + sign*amp*math.sin(2*math.pi*1.25*(y-(100-r))/(2*r)), y))
    return pts
h1, h2 = helix_pts(1), helix_pts(-1)
hd = lambda p: "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in p)
rung = "".join(path(f"M{h1[i][0]:.2f} {h1[i][1]:.2f}L{h2[i][0]:.2f} {h2[i][1]:.2f}", "a2", 1.1) for i in range(4, 78, 4))
emblem("Helix Meridians", "Engraved instrument",
       "A globe whose meridians are the two strands of a DNA helix, with the base pairs drawn as rungs across them. Inside a beaded ring.",
       circ(92, "ink", 1) + beads(86, 60, 1.3) + circ(80, "ink", 1.6) +
       shaded(crescent(100, 100, 60, .3, -.3), -45, 2.6, .7) + rung + path(hd(h1), "ink", 3) + path(hd(h2), "a1", 3) + circ(60, "ink", 2.6),
       circ(80, "ink", 10) + path(hd(helix_pts(1, 80, 60)), "ink", 9) + path(hd(helix_pts(-1, 80, 60)), "a1", 9))

# 9 Sun & Lens
lens_grid = "".join(path(f"M{v} 40V150M40 {v}H150", "a2", .8) for v in range(52, 140, 10))
emblem("Sun & Lens", "Engraved instrument",
       "A magnifying glass held up against a rising sun, with a single star in focus inside the lens. The search, and the moment of finding.",
       rays(30, 92, 80, 64, "ink", 1) + circ(37, None, 0, 90, 90, fill_c="ground") +
       clip('<circle cx="90" cy="90" r="34"/>', lens_grid + shaded(crescent(90, 90, 34, .35, .35), 45, 3, .6, "ink")) +
       star(92, 86, 8, "a1") + circ(36, "ink", 5, 90, 90) + circ(31, "ink", .8, 90, 90) +
       path("M116 116L156 156", "ink", 11) + path("M118 118L124 124M148 148L154 154", "a1", 12, extra='stroke-linecap="butt"'),
       rays(56, 96, 84, 16, "ink", 6) + circ(48, None, 0, 86, 86, fill_c="ground") + circ(46, "ink", 12, 86, 86) +
       star(86, 86, 18, "a1") + path("M122 122L170 170", "ink", 20))

# 10 Cartographer's Dividers
earth = clip('<circle cx="100" cy="100" r="86"/>',
             f'<circle cx="100" cy="250" r="110" {fill("ground")}/>' +
             globe(100, 250, 110, lw=1, outline=2.4, lat=(-75, -60, -45), mer=(15, 30, 45), shade=False) +
             "")
leg = lambda sx: poly([(100-3, 46), (100+3, 46), (100+sx*34+.8, 148), (100+sx*34-.8, 148)][::1] if sx > 0 else [(100-3, 46), (100+3, 46), (100+sx*34+.8, 148), (100+sx*34-.8, 148)], "ink")
emblem("Dividers & Horizon", "Engraved vignette",
       "A pair of map dividers measuring across the curve of the Earth under a few stars. This is how distance was taken off an atlas page.",
       circ(92, "ink", 1) + circ(86, "ink", 2.2) + earth +
       clip('<circle cx="100" cy="100" r="86"/>', path("M14 154Q100 128 186 154", "ink", 1.8)) +
       poly([(97, 46), (103, 46), (66.8, 147), (65.2, 147)]) + poly([(97, 46), (103, 46), (134.8, 147), (133.2, 147)]) +
       circ(8, "ink", 3, 100, 42, fill_c="ground") + dot(100, 42, 2.4, "a1") +
       path("M73 122Q100 110 127 122", "a1", 1.6, extra='stroke-dasharray="2 3"') +
       sparkle(48, 60, 4, "a1") + sparkle(152, 70, 3, "a1") + dot(60, 92, 1.2, "a1") + dot(140, 40, 1.4, "a1") + dot(160, 104, 1, "a1"),
       f'<path d="M14 168Q100 126 186 168" fill="none" {strk("a1")} stroke-width="9"/>' +
       poly([(92, 30), (108, 30), (54, 176), (46, 176)]) + poly([(92, 30), (108, 30), (154, 176), (146, 176)]) + circ(15, "ink", 8, 100, 30, fill_c="ground"))

# 11 Celestial Flask
cf = rflask(100, 116, 52, 20, 36)
cstars = [(84, 150, 3.4), (100, 92, 4.6), (116, 150, 3.4), (90, 124, 2.4), (110, 124, 2.4), (70, 104, 1.6), (132, 98, 1.8), (78, 136, 1.2), (128, 132, 1.4), (100, 160, 1.2)]
emblem("Celestial Flask", "Engraved instrument",
       "A round flask full of night sky, with a constellation inside that traces an A. Discovery, drawn the way star atlases drew it.",
       clip(f'<circle cx="100" cy="116" r="50"/>', hatch_lines(0, 2.2, .7, "ink") +
            path("M84 150L100 92L116 150M90 124H110", "a1", .9, extra='opacity=".9"') +
            "".join(circ(r+1.6, None, 0, x, y, fill_c="ground") + (star(x, y, r*1.8, "a1") if r > 3 else dot(x, y, r, "a1")) for x, y, r in cstars)) +
       path(cf, "ink", 3) + path("M86 36H114", "ink", 3) + sparkle(100, 20, 6, "a1") + sparkle(150, 54, 3.5, "a1") + sparkle(50, 62, 3, "a1"),
       clip('<circle cx="100" cy="118" r="62"/>', f'<rect width="200" height="200" {fill("ink")}/>' + star(100, 112, 30, "ground")) +
       path(rflask(100, 118, 64, 30, 18), "ink", 10) + path("M78 18H122", "ink", 10))

# 12 Mountain & Meridian
mts = [(14, 150), (62, 82), (84, 108), (112, 64), (186, 150)]
emblem("Summit & Sun", "Engraved vignette",
       "Fieldwork as a vignette: an engraved mountain against a sun rising inside a graticule, with water lines below. It stands for the field, the third kind of lab.",
       circ(92, "ink", 1) + circ(86, "ink", 2.4) +
       clip('<circle cx="100" cy="100" r="85"/>',
            "".join(path(f"M10 {y}Q100 {y-14} 190 {y}", "a2", .8) for y in range(40, 140, 14)) +
            circ(26, None, 0, 132, 118, fill_c="ground") + rays(30, 52, 42, 24, "a1", 1.2, 132, 118, 180, 360) + dot(132, 118, 24, "a1") +
            poly(mts + [(186, 200), (14, 200)], "ground") +
            masked('<path d="M112 64L186 150H120L96 118Z" fill="#fff"/><path d="M62 82L84 108L74 150H40Z" fill="#fff"/>', hatch_lines(60, 2.6, .9, "ink")) +
            path("M" + "L".join(f"{x} {y}" for x, y in mts), "ink", 2.2) + path("M102 76L112 64L124 78L116 76L112 82L106 76Z", "ink", 1, "ink") +
            "".join(path("M10 {0}".format(y) + "".join(f"Q{x+5} {y-3} {x+10} {y}T{x+20} {y}" for x in range(10, 190, 20)), "ink", .9) for y in range(158, 190, 7))),
       clip('<circle cx="100" cy="100" r="92"/>', f'<circle cx="100" cy="100" r="92" {fill("ground")}/>' + dot(140, 112, 30, "a1") +
            poly([(-4, 160), (66, 66), (96, 104), (122, 48), (204, 160), (204, 204), (-4, 204)], "ink")) )

# 13 Petri Map
isl, irad = blob(98, 104, 36, .26, 11)
ripples = "".join(path(blob(98, 104, 36+k*5, .26*(36/(36+k*5)), 11)[0], "ink", .8, extra=f'opacity="{1-k*.18:.2f}"') for k in range(1, 5))
emblem("Petri Atlas", "Engraved vignette",
       "A petri dish drawn as an old coastal chart: a stippled island, ripple lines along its shore, and a small compass rose. Culture and cartography.",
       circ(84, "ink", 3.4) + circ(77, "ink", 1) + clip('<circle cx="100" cy="100" r="76"/>', ripples) +
       f'<path d="{isl}" {fill("ground")} {strk("ink")} stroke-width="1.8"/>' + stipple(98, 104, irad, 260, 1, "ink", 3, .95) +
       rose(144, 58, [(4, 13, 3, -90)], w=.6) + dot(66, 76, 2, "a1") + circ(5, "a1", 1.2, 66, 76),
       circ(84, "ink", 10) + f'<path d="{blob(98, 104, 46, .26, 11)[0]}" {fill("a1")}/>')

# 14 Astrolabe
alm = "".join(circ(60 - k*7, "a2", .8, 100, 100 - k*8) for k in range(0, 7))
emblem("Astrolabe", "Engraved instrument",
       "An astrolabe face: graduated rim, the curved altitude lines on the plate, the offset ring of the zodiac and a pointer. It was the original instrument for finding where you are.",
       f'<circle cx="100" cy="18" r="8" fill="none" {strk("ink")} stroke-width="3"/>' + path("M94 26H106", "ink", 4) +
       circ(82, "ink", 3, 100, 108) + ticks(72, 4, 9, 72, 6, "ink", .9, 100, 108) + circ(72, "ink", 1, 100, 108) +
       clip('<circle cx="100" cy="108" r="71"/>', "".join(circ(60 - k*7, "a2", .8, 100, 108 - k*8) for k in range(7)) + circ(46, "ink", 1, 100, 108) + circ(24, "ink", 1, 100, 108)) +
       circ(44, "a1", 2.4, 100, 96) + "".join(sparkle(*pt(a, 44, 100, 96), 3.2, "a1") for a in (-150, -60, 20, 110)) +
       f'<g transform="rotate(-38 100 108)"><path d="M28 108L100 103L172 108L100 113Z" {fill("ink")}/></g>' + circ(4.5, "ink", 2, 100, 108, fill_c="ground"),
       circ(76, "ink", 10, 100, 112) + circ(16, "ink", 7, 100, 18) + circ(42, "a1", 8, 100, 100) +
       f'<g transform="rotate(-38 100 112)"><path d="M18 112L100 104L182 112L100 120Z" {fill("ink")}/></g>')

# 15 Alembic
neck = "M84 90Q120 52 160 138L153 142Q118 72 97 102Z"
emblem("Retort", "Engraved instrument",
       "An alchemist's retort over a small flame, with a hatched liquid line, inside a beaded seal. It nods to the long history of the lab.",
       circ(92, "ink", 1) + beads(87, 64, 1.1) + circ(82, "ink", 2) +
       f'<path d="{neck}" {fill("ground")} {strk("ink")} stroke-width="2.6" stroke-linejoin="round"/>' +
       circ(30, "ink", 2.8, 70, 112, fill_c="ground") +
       masked(f'<circle cx="70" cy="112" r="29" fill="#fff"/><rect width="200" height="116" fill="#000"/>', hatch_lines(25, 2.6, .9, "ink")) +
       path("M41 116Q70 122 99 116", "ink", 1.4) +
       path("M52 140L47 152M88 140L93 152M40 152H100", "ink", 2.2) +
       f'<path d="M70 172C62 164 66 157 70 152C74 157 78 164 70 172Z" {fill("a1")}/>' +
       f'<path d="M140 140h26l-3 14h-20z" fill="none" {strk("ink")} stroke-width="1.8" stroke-linejoin="round"/>' + dot(156.5, 150, 2, "a1") +
       sparkle(128, 42, 5, "a1") + sparkle(150, 70, 3, "a1"),
       circ(42, "ink", 11, 66, 104) + path("M90 72Q134 30 176 156", "ink", 12) + f'<path d="M66 192C54 182 58 170 66 160C74 170 78 182 66 192Z" {fill("a1")}/>')

# 16 Open Atlas
lp = "M100 156C80 146 52 146 26 152V106C52 100 80 100 100 110Z"
rp = "M100 156C120 146 148 146 174 152V106C148 100 120 100 100 110Z"
plines = "".join(path(f"M{30 if s<0 else 170} {y}C{56 if s<0 else 144} {y-6} {82 if s<0 else 118} {y-6} 100 {y+4}", "a2", .7) for s in (-1, 1) for y in range(114, 150, 6))
emblem("Open Atlas", "Engraved vignette",
       "An open atlas with a globe rising out of it in a burst of light. The globe sits on the spine, so the book and the world form one shape.",
       rays(36, 76, 64, 40, "a1", 1, 100, 72, 180, 360) + globe(100, 72, 30) +
       f'<path d="{lp}" {fill("ground")}/><path d="{rp}" {fill("ground")}/>' + plines +
       path(lp, "ink", 2.4) + path(rp, "ink", 2.4) + path("M26 152C52 146 80 148 100 160C120 148 148 146 174 152", "ink", 1.2) + path("M100 110V160", "ink", 1.6),
       globe(100, 64, 44, lw=4, outline=9, lat=(0,), mer=(60,), shade=False) +
       path("M100 176C76 162 42 162 12 170V116C42 108 76 108 100 122C124 108 158 108 188 116V170C158 162 124 162 100 176Z", "ink", 0, "ink"))

# 17 Crest Quadrants
q = lambda x, y: (x, y)
emblem("Quartered Crest", "Heraldic crest",
       "A shield quartered like a coat of arms: a globe, a flask, a star and contour lines. The four parts of the product in one crest.",
       clip(f'<path d="{shield_d()}"/>',
            clip('<rect x="104" y="28" width="60" height="68"/>', hatch_lines(0, 2.6, .8, "ink")) +
            clip('<rect x="36" y="102" width="64" height="80"/>', hatch_lines(90, 2.6, .8, "ink")) +
            f'<path d="M94 28H106V180H94Z M36 92H164V104H36Z" {fill("a1")}/>' +
            "".join(path(blob(132, 138, R, .14, 4)[0], "ink", 1) for R in (8, 16, 24, 32))) +
       globe(66, 60, 20, lw=.8, outline=1.6) + f'<circle cx="134" cy="62" r="20" {fill("ground")}/>' +
       path(rflask(134, 66, 15, 8, 40), "ink", 2.2) + path("M128 40H140", "ink", 2.2) + star(68, 136, 15, "ink") +
       path(shield_d(), "ink", 3) + path(shield_d(46, 154, 34, 98, 170), "ink", .8),
       clip(f'<path d="{shield_d(24, 176, 14, 96, 192)}"/>', f'<path d="M88 0H112V200H88Z M0 84H200V108H0Z" {fill("a1")}/>' +
            f'<rect x="112" y="0" width="100" height="84" {fill("ink")}/><rect x="0" y="108" width="88" height="100" {fill("ink")}/>') +
       path(shield_d(24, 176, 14, 96, 192), "ink", 10))

# 18 Meridian A
emblem("Meridian A", "Monogram seal",
       "Two meridians meet at the north pole to form an A, and the equator is its crossbar, set on a fully engraved globe in a beaded ring.",
       circ(92, "ink", 1) + beads(86, 60, 1.2) + circ(80, "ink", 1.8) +
       globe(100, 100, 66, c="a2", lw=.8, outline=1.4, lat=(-60, -30, 30, 60), mer=(20, 45, 70)) +
       path("M100 34Q66 70 62 154M100 34Q134 70 138 154", "ink", 6) + path("M64 108Q100 120 136 108", "a1", 5) + star(100, 34, 7, "a1"),
       circ(84, "ink", 8) + path("M100 16Q52 64 48 176M100 16Q148 64 152 176", "ink", 14) + path("M50 112Q100 130 150 112", "a1", 12))

# 19 Molecule Constellation
hexs = [pt(-90 + i*60, 34, 100, 112) for i in range(6)]
rnd = random.Random(19)
field = "".join(dot(rnd.uniform(20, 180), rnd.uniform(20, 180), rnd.uniform(.4, 1), "a2") for _ in range(150))
emblem("Benzene Constellation", "Celestial chart",
       "A benzene ring drawn as a constellation on a star chart. One bond reaches up to a bright star, the way old charts joined stars into figures.",
       circ(92, "ink", 1) + ticks(84, 3, 7, 120, 10, "ink", .7) + circ(84, "ink", 2) +
       clip('<circle cx="100" cy="100" r="83"/>', field + path(f"M{hexs[0][0]:.1f} {hexs[0][1]:.1f}L100 44", "ink", 1) + path("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in hexs) + "Z", "ink", 1.1) +
            circ(20, "ink", .8, 100, 112, extra='stroke-dasharray="1.5 3"')) +
       "".join(circ(5.2, None, 0, x, y, fill_c="ground") + star(x, y, 6, "a1") for x, y in hexs) + sparkle(100, 40, 12, "a1"),
       path("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in [pt(-90 + i*60, 62) for i in range(6)]) + "Z", "ink", 8) +
       "".join(dot(*pt(-90 + i*60, 62), 15, "a1") for i in range(6)))

# 20 Wax Seal
wd, _ = blob(100, 100, 84, .05, 21, 220)
wd2 = "M" + "L".join(f"{100 + (84 + 3.2*math.sin(14*t))*math.cos(t):.2f} {100 + (84 + 3.2*math.sin(14*t))*math.sin(t):.2f}" for t in [2*math.pi*i/280 for i in range(280)]) + "Z"
emblem("Wax Seal", "Seal",
       "A pressed wax seal with a flask-globe stamped into it and a ring of beads around the edge, like the seal on a letter of admission.",
       f'<path d="{wd2}" {fill("a3")}/>' + circ(66, "ground", 2.2) + beads(60, 40, 1.4, "ground") + circ(54, "ground", 1) +
       path(rflask(100, 108, 26, 12, 64), "ground", 3) + path("M92 64H108", "ground", 3) + path("M76 112Q100 120 124 112", "ground", 1.6) +
       f'<ellipse cx="100" cy="108" rx="10" ry="26" fill="none" {strk("ground")} stroke-width="1.2"/>' +
       path("M48 64Q58 46 76 40", "a1", 2.6, extra='opacity=".55"'),
       f'<path d="{wd2}" {fill("a3")}/>' + path(rflask(100, 112, 38, 20, 40), "ground", 10) + path("M86 40H114", "ground", 10))

# 21 Navigator's Pin
pin = "M100 182C82 152 50 122 50 84A50 50 0 0 1 150 84C150 122 118 152 100 182Z"
emblem("Navigator's Pin", "Cartographic ornament",
       "A map pin engraved like a brass instrument. The head is a globe and the point lands in a graduated target ring.",
       f'<ellipse cx="100" cy="182" rx="40" ry="9" fill="none" {strk("a2")} stroke-width="1"/>' + f'<ellipse cx="100" cy="182" rx="24" ry="5" fill="none" {strk("a2")} stroke-width="1"/>' +
       f'<path d="{pin}" {fill("ground")}/>' + masked(f'<path d="{pin}" fill="#fff"/><rect x="0" y="0" width="100" height="200" fill="#000"/>', hatch_lines(0, 2.4, .8, "ink")) +
       path(pin, "ink", 3) + circ(36, None, 0, 100, 84, fill_c="ground") + globe(100, 84, 34) + sparkle(160, 30, 5, "a1"),
       f'<path d="M100 196C76 160 30 126 30 80A70 70 0 0 1 170 80C170 126 124 160 100 196Z" {fill("ink")}/>' + dot(100, 80, 38, "ground") + dot(100, 80, 26, "a1"))

# 22 Crossed Instruments
scope = (f'<g transform="rotate(-45 100 100)">'
         + poly([(34, 94), (80, 95.5), (80, 104.5), (34, 106)], "ink") + poly([(82, 93), (124, 94), (124, 106), (82, 107)], "ink")
         + poly([(126, 91.5), (168, 92), (168, 108), (126, 108.5)], "ink") + path("M81 93V107M125 91V109", "a1", 2.4) + '</g>')
pip = (f'<g transform="rotate(45 100 100)">' + f'<ellipse cx="44" cy="100" rx="13" ry="10" {fill("a1")}/>'
       + poly([(56, 97), (150, 98.6), (166, 100), (150, 101.4), (56, 103)], "a1") + "".join(path(f"M{x} 96.4V99", "ground", .9) for x in range(70, 146, 8)) + '</g>')
emblem("Crossed Instruments", "Heraldic crest",
       "A telescope and a pipette crossed behind a small globe, like the crossed tools on a guild crest. Looking out and looking closer.",
       rays(46, 92, 80, 48, "a2", .8) + scope + pip + circ(30, None, 0, 100, 100, fill_c="ground") + globe(100, 100, 26) +
       wreath(70, 100, 4, "ink", cy=112),
       f'<g transform="rotate(-45 100 100)"><rect x="6" y="88" width="188" height="24" rx="3" {fill("ink")}/></g>' +
       f'<g transform="rotate(45 100 100)"><rect x="6" y="91" width="188" height="18" rx="9" {fill("a1")}/></g>' + dot(100, 100, 40, "ground") + dot(100, 100, 28, "ink"))

# 23 Guilloche Rosette
def guil(R, r, d, rot, n=900, cx=CX, cy=CY):
    pts = []
    for i in range(n+1):
        t = 2*math.pi*r*i/n * (1 if True else 1)
        t = i/n * 2*math.pi*r/math.gcd(int(R), int(r))
        x = (R-r)*math.cos(t) + d*math.cos((R-r)/r*t)
        y = (R-r)*math.sin(t) - d*math.sin((R-r)/r*t)
        a = math.radians(rot)
        pts.append((cx + x*math.cos(a) - y*math.sin(a), cy + x*math.sin(a) + y*math.cos(a)))
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
emblem("Guilloché Rosette", "Engraved ornament",
       "A guilloché rosette, the machine-engraved pattern on banknotes and certificates, around a round flask. It makes the mark feel like an official credential.",
       path(guil(60, 6, 28, 0), "ink", .6) + path(guil(60, 6, 28, 15), "a2", .6) + path(guil(44, 4, 16, 0), "a1", .6) +
       circ(88, "ink", 1) + circ(28, "ink", 2.4, fill_c="ground") +
       path(rflask(100, 104, 14, 8, 82), "ink", 2.4) + path("M94 82H106", "ink", 2.4),
       path(guil(60, 10, 30, 0, 400), "ink", 3.6) + circ(40, "ink", 6, fill_c="ground") + path(rflask(100, 108, 22, 12, 72), "a1", 7))

# 24 Double Hemisphere
def hemi(cx):
    land1, lr1 = blob(cx-6, 92, 14, .5, cx)
    land2, lr2 = blob(cx+10, 118, 10, .5, cx+1)
    return (globe(cx, 104, 38, c="a2", lw=.7, outline=0, shade=False) +
            clip(f'<circle cx="{cx}" cy="104" r="38"/>', f'<path d="{land1}" {fill("ground")} {strk("ink")} stroke-width="1.2"/>' + stipple(cx-6, 92, lr1, 70, .8, "ink", cx)
                 + f'<path d="{land2}" {fill("ground")} {strk("ink")} stroke-width="1.2"/>' + stipple(cx+10, 118, lr2, 40, .8, "ink", cx+3)) +
            circ(38, "ink", 2.4, cx, 104) + circ(42, "ink", .8, cx, 104))
emblem("Two Hemispheres", "Cartographic ornament",
       "The double-hemisphere world map from old atlas title pages, with stippled continents, joined by a ribbon and crowned with a star.",
       hemi(56) + hemi(144) + path("M98 104H102", "ink", 2) +
       path("M56 146Q100 172 144 146", "ink", 1.6) + path("M60 152Q100 176 140 152", "a1", 3) +
       path("M56 62Q100 30 144 62", "ink", 1) + star(100, 40, 9, "a1") + sparkle(78, 46, 3, "a1") + sparkle(122, 46, 3, "a1"),
       circ(44, "ink", 9, 52, 100) + circ(44, "ink", 9, 148, 100) + dot(52, 100, 26, "a1") + dot(148, 100, 26, "a1"))

# ------------------------------------------------------------- output
def svg(body, size, key):
    return f'<svg viewBox="0 0 200 200" width="{size}" height="{size}" aria-hidden="true">{body.replace("@@", f"e{key}-")}</svg>'

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def export():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for key, p in PALETTES.items():
        for e in E:
            for kind in ("full", "core"):
                body = e[kind].replace("@@", "e")
                body = re.sub(r'style="([^"]*)"', lambda m: " ".join(f'{k}="{p[v]}"' for k, v in re.findall(r'(fill|stroke):var\(--(\w+)\)', m.group(1))), body)
                doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="400" height="400">'
                       f'<title>{html.escape(e["name"])}</title><rect width="200" height="200" fill="{p["ground"]}"/>'
                       f'<g transform="translate(14 14) scale(.86)">{body}</g></svg>\n')
                suffix = "" if kind == "full" else "-small"
                with open(os.path.join(out, f"{e['n']:02d}-{slug(e['name'])}-{key}{suffix}.svg"), "w") as fh:
                    fh.write(doc)

CSS = r"""
/* Layout: an atlas plate catalogue. Brief, palette key, then one plate per emblem showing both palettes side by side. */
:root{
  --bg:#f4efe3; --surface:#fbf8f0; --fg:#231c14; --fg2:#6b5f4f; --rule:#dfd4bd; --accent:#8e4f2f;
  --sans:'Atlas Text',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;
  --serif:'Cormorant Garamond','Iowan Old Style',Georgia,serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0b1420;--surface:#111d2c;--fg:#ece6d6;--fg2:#a49a86;--rule:#26364a;--accent:#d4a72c;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0b1420;--surface:#111d2c;--fg:#ece6d6;--fg2:#a49a86;--rule:#26364a;--accent:#d4a72c;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1240px;margin:0 auto;padding-inline:clamp(16px,4vw,40px);padding-block:48px 72px}
.intro{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:40px;align-items:end;padding-bottom:28px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg2);margin:0 0 10px}
h1{font-family:var(--serif);font-weight:500;font-style:italic;font-size:clamp(40px,6vw,72px);line-height:.98;letter-spacing:-.01em;margin:0;text-wrap:balance}
.lede{color:var(--fg2);max-width:60ch;margin:0}
.keys{display:flex;flex-wrap:wrap;gap:20px;margin-top:16px}
.key{display:flex;gap:8px;align-items:center;font-size:13px}
.key i{display:inline-flex;border-radius:999px;overflow:hidden;box-shadow:0 0 0 1px var(--rule)}
.key b{display:block;width:14px;height:14px}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);display:flex;flex-wrap:wrap;gap:10px 20px;align-items:center;justify-content:space-between;padding-block:12px;border-bottom:1px solid var(--rule)}
.seg{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.seg .lbl{font-size:12px;color:var(--fg2);letter-spacing:.08em;text-transform:uppercase;margin-right:4px}
.seg button{font:inherit;font-size:13px;color:var(--fg);background:transparent;border:1px solid var(--rule);border-radius:999px;padding:6px 12px;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.seg button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.plates{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px;padding-top:28px}
.plate{background:var(--surface);border:1px solid var(--rule);border-radius:4px;display:flex;flex-direction:column;min-width:0}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--rule)}
.plates[data-show="navy"] .pair,.plates[data-show="earth"] .pair{grid-template-columns:1fr}
.plates[data-show="navy"] .t-earth,.plates[data-show="earth"] .t-navy{display:none}
.tile{aspect-ratio:1/1;max-width:100%;display:grid;place-items:center;background:var(--ground)}
.tile svg{width:88%;height:88%}
.t-navy{--ground:#031b36;--ink:#d4a72c;--a1:#fdffee;--a2:#8c6d1f;--a3:#e9cf86}
.t-earth{--ground:#f1e7d0;--ink:#2e2419;--a1:#b07d2a;--a2:#7f8a62;--a3:#8e4f2f}
.meta{padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px;flex:1}
.row{display:flex;align-items:baseline;gap:10px}
.no{font-family:var(--serif);font-style:italic;font-size:18px;color:var(--fg2);font-variant-numeric:tabular-nums}
.plate h3{margin:0;font-family:var(--serif);font-weight:600;font-size:22px;line-height:1.1}
.why{margin:0;color:var(--fg2);font-size:13.5px;line-height:1.5;flex:1}
.foot{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.method{font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--fg2)}
.small{display:flex;gap:6px;align-items:center}
.small .lbl{font-size:11px;color:var(--fg2);margin-right:2px}
.chip{display:grid;place-items:center;border-radius:7px;background:var(--ground)}
.chip.c32{width:32px;height:32px}.chip.c16{width:16px;height:16px;border-radius:4px}
.chip.c32 svg{width:28px;height:28px}.chip.c16 svg{width:14px;height:14px}
.notes{margin-top:56px;padding-top:28px;border-top:1px solid var(--rule);display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:28px}
.notes h4{margin:0 0 6px;font-family:var(--serif);font-weight:600;font-size:19px}
.notes p{margin:0;color:var(--fg2);font-size:14px;max-width:60ch}
@media (max-width:760px){.intro{grid-template-columns:minmax(0,1fr);gap:18px}.plates{grid-template-columns:minmax(0,1fr)}}
"""

def page(fonts_css, full_doc):
    plates = []
    for e in E:
        tiles = "".join(f'<div class="tile t-{k}">{svg(e["full"], 200, f"{e["n"]}{k}f")}</div>' for k in PALETTES)
        chips = "".join(f'<span class="chip c32 t-{k}">{svg(e["core"], 28, f"{e["n"]}{k}a")}</span><span class="chip c16 t-{k}">{svg(e["core"], 14, f"{e["n"]}{k}b")}</span>' for k in PALETTES)
        plates.append(f'''<article class="plate">
  <div class="pair">{tiles}</div>
  <div class="meta">
    <div class="row"><span class="no">{e['n']:02d}</span><h3>{html.escape(e['name'])}</h3></div>
    <p class="why">{html.escape(e['why'])}</p>
    <div class="foot"><span class="method">{html.escape(e['method'])}</span><span class="small" title="Small-size version at 32 and 16 pixels"><span class="lbl">Small</span>{chips}</span></div>
  </div>
</article>''')
    keys = "".join(f'<span class="key"><i>{"".join(f"<b style=background:{p[c]}></b>" for c in ("ground", "ink", "a1", "a2", "a3"))}</i>{p["name"]}</span>' for p in PALETTES.values())
    body = f'''<div class="wrap">
  <div class="intro">
    <div><p class="eyebrow">Lab Atlas · identity, round two</p><h1>Emblems from an atlas plate</h1></div>
    <div>
      <p class="lede">These 24 emblems are drawn the way old atlas plates and academic seals were: hatching, stipple, graduated rims, laurels and stars. Each is shown in two sample palettes. Fine engraving disappears at icon size, so every emblem also has a simplified small version, shown at 32 and 16 pixels on each card.</p>
      <div class="keys">{keys}</div>
    </div>
  </div>
  <div class="bar">
    <div class="seg" role="group" aria-label="Palette"><span class="lbl">Palette</span>
      <button type="button" id="p-both" data-show="both" aria-pressed="true">Both</button>
      <button type="button" id="p-navy" data-show="navy" aria-pressed="false">Navy &amp; gold</button>
      <button type="button" id="p-earth" data-show="earth" aria-pressed="false">Earth</button>
    </div>
  </div>
  <main class="plates" id="plates" data-show="both">
{chr(10).join(plates)}
  </main>
  <div class="notes">
    <div><h4>Two palettes</h4><p>Navy &amp; gold keeps the product's navy and gold, with cream for highlights. Earth uses a sepia ink on parchment, with ochre, sage and burnt sienna. Neither uses the old blue, pink and red.</p></div>
    <div><h4>Full emblem and small mark</h4><p>The full emblem is for the homepage, social cards, stickers and print. The small mark keeps only the emblem's central device, for favicons and app icons.</p></div>
    <div><h4>Strongest candidates</h4><p>Armillary Flask, Globe on an A, Celestial Flask and Meridian A each read as lab and atlas at once. Globe Seal and Wax Seal are the most seal-like. Astrolabe and Portolan Rose lean furthest toward the old atlas.</p></div>
  </div>
</div>
<script>
(function(){{
  var g=document.getElementById('plates');
  var bs=[].slice.call(document.querySelectorAll('[data-show]')).filter(function(b){{return b.tagName==='BUTTON'}});
  function set(v){{g.dataset.show=v;bs.forEach(function(b){{b.setAttribute('aria-pressed',String(b.dataset.show===v))}});try{{localStorage.setItem('la-em-show',v)}}catch(e){{}}}}
  bs.forEach(function(b){{b.addEventListener('click',function(){{set(b.dataset.show)}})}});
  try{{var v=localStorage.getItem('la-em-show');if(v==='navy'||v==='earth'||v==='both')set(v)}}catch(e){{}}
}})();
</script>'''
    fonts_link = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap">'
    head = f'<title>Lab Atlas Emblems</title>\n{fonts_link}\n<style>\n{fonts_css}\n{CSS}\n</style>'
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

if __name__ == "__main__":
    assert len(E) == 24, len(E)
    fonts = open(sys.argv[1]).read() if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else ""
    export()
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page(fonts, True))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            f.write(page(fonts, False))
    print("built", len(E), "emblems")
