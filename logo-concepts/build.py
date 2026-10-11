"""Build the Lab Atlas logo-concept gallery and per-mark SVG files.

Usage: python3 build.py [path/to/atlas-text.css] [artifact-out.html]

Every mark is drawn on a 64x64 grid. Ink uses currentColor and accents use
CSS variables, so the gallery can show each mark on a navy or a paper ground.
The exported SVGs bake in the navy-ground colours.
"""
import math, os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))

# One accent (gold) plus the ink in two softer tones. Ground colours come from the live product.
GROUNDS = {
    "navy":  {"ink": "#fdffee", "gold": "#d4a72c", "tone": "#9ea8a8", "mist": "#5a6b76", "ground": "#031b36", "bg": "#031b36"},
    "paper": {"ink": "#031b36", "gold": "#b98a12", "tone": "#62727c", "mist": "#a6afae", "ground": "#fdffee", "bg": "#fdffee"},
}

def F(c): return f'style="fill:var(--{c})"'
def S(c): return f'style="stroke:var(--{c})"'
INK = 'currentColor'
LINE = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'

def stroke(d, w=5, c=None, extra=""):
    col = f'stroke="{INK}"' if c is None else S(c)
    return f'<path d="{d}" {LINE} {col} stroke-width="{w}" {extra}/>'

def dot(x, y, r, c=None, extra=""):
    col = f'fill="{INK}"' if c is None else F(c)
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" {col} {extra}/>'

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))

def qbez(p0, p1, p2, t):
    u = 1 - t
    return tuple(u*u*a + 2*u*t*b + t*t*c for a, b, c in zip(p0, p1, p2))

def x_at_y(curve, y, n=400):
    best = min((abs(bez(*curve, i/n)[1]-y), bez(*curve, i/n)[0]) for i in range(n+1))
    return best[1]

# ---------------------------------------------------------------- marks
M = []
def mark(name, group, method, why, svg, pick=False):
    M.append(dict(n=len(M)+1, name=name, group=group, method=method, why=why, svg=svg, pick=pick))

# I. Initials ----------------------------------------------------------
mark("Single Line", "initials", "Monogram",
     "L and A drawn as one unbroken stroke: the L's foot runs straight into the A's first leg.",
     stroke("M16 12V52H30L42 12L54 52", 5) + stroke("M34.2 38H49.8", 5, "gold"))

g = ((17, 50), (27, 50), (28.5, 13), (33, 13)); g2 = ((33, 13), (37.5, 13), (39, 50), (49, 50))
yh = 31.5
mark("Axes & Peak", "initials", "Monogram + meaning",
     "The L is a chart's axes, the A is a measured peak, and its crossbar is the half-height line every bench scientist reads.",
     stroke("M12 9V53H56", 4.5) +
     stroke("M17 50C27 50 28.5 13 33 13C37.5 13 39 50 49 50", 4.5, "gold") +
     stroke(f"M{x_at_y(g, yh)+4:.1f} {yh}H{x_at_y(g2, yh)-4:.1f}", 3.5, "tone"), pick=True)

mark("Drafting Compass", "initials", "Metaphor fusion",
     "A cartographer's compass is an A: hinge at the apex, two legs, and the arc it draws as the crossbar.",
     f'<circle cx="32" cy="12" r="4.5" fill="none" stroke="{INK}" stroke-width="4"/>' +
     stroke("M30 16.5L16 54M34 16.5L46 50L48 55", 4.5) + stroke("M21.5 40Q32 47 42.5 40", 3.5, "gold"))

mark("Pole A", "initials", "Monogram + meaning",
     "Two meridians meet at the north pole to make the A; the equator is its crossbar.",
     f'<circle cx="32" cy="32" r="24" fill="none" stroke="{INK}" stroke-width="2.5" opacity=".3"/>' +
     stroke("M32 8Q18 28 16.5 49M32 8Q46 28 47.5 49", 4.5) + stroke("M18.5 35Q32 41 45.5 35", 4, "tone"), pick=True)

mark("Atlas A", "initials", "Metaphor fusion",
     "The titan reduced to a letter: an A carrying a globe on its apex.",
     stroke("M14 56L32 31L50 56", 5) + stroke("M21 46H43", 4) +
     dot(32, 18, 11, "tone") + stroke("M21.5 18Q32 22 42.5 18", 2.2, "ground"))

ticks = "".join(f'<path d="M18 {y}H{24 if i%2 else 28}" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>' for i, y in enumerate(range(14, 46, 6)))
mark("Graduated L", "initials", "Monogram + meaning",
     "An L marked like a graduated cylinder, with a single drop beside it: the bench in one letter.",
     stroke("M18 8V50H54", 5.5) + ticks +
     f'<path d="M42 17C42 17 34 27 34 33a8 8 0 0 0 16 0C50 27 42 17 42 17Z" {F("gold")}/>')

mark("Corner & Summit", "initials", "Construction",
     "A map's corner registration mark is the L; the summit it frames is the A.",
     stroke("M10 20V54H44", 5) + f'<path d="M24 46L40 16L56 46Z" {F("tone")} stroke-linejoin="round"/>' +
     f'<path d="M34.7 26L40 16L45.3 26L42.5 24L40 27L37.5 24Z" fill="{INK}"/>')

mark("Doorway A", "initials", "Negative space",
     "A pointed arch read as an A, with a lit doorway in place of the counter: the way into a lab.",
     stroke("M14 56V36A30 30 0 0 1 32 8A30 30 0 0 1 50 36V56", 5) +
     f'<path d="M26 56V44a6 6 0 0 1 12 0V56Z" {F("gold")}/>')

L = [(12, 12), (12, 50), (26, 50)]; A = [(26, 50), (39, 13), (52, 50)]
cx1, cx2 = 26+(14/37)*13, 39+(23/37)*13
lines = stroke("M12 12L12 50L26 50L39 13L52 50", 1.8, extra='opacity=".55"') + stroke(f"M{cx1:.1f} 36H{cx2:.1f}", 1.8, extra='opacity=".55"')
stars = "".join(dot(x, y, 2.8) for x, y in [(12, 12), (12, 50), (26, 50), (52, 50), (cx1, 36), (cx2, 36)]) + dot(39, 13, 4.4, "gold")
mark("Constellation", "initials", "Construction",
     "Seven stars drawn into L and A, the way old atlases joined stars into figures.", lines + stars)

mark("Cutout LA", "initials", "Negative space",
     "A solid block with L and A knocked out of it. Works as an app icon on any ground.",
     '<mask id="@@m"><rect width="64" height="64" fill="#fff"/>'
     '<path d="M16 15V47H28" fill="none" stroke="#000" stroke-width="6" stroke-linecap="square"/>'
     '<path d="M32 49L40.5 15L49 49M35 38H46" fill="none" stroke="#000" stroke-width="5.5" stroke-linejoin="miter"/></mask>'
     f'<rect x="7" y="7" width="50" height="50" rx="11" fill="{INK}" mask="url(#@@m)"/>')

mark("Ball-and-Stick A", "initials", "Metaphor fusion",
     "An A built like a molecular model: bonds for strokes, atoms at the joints.",
     stroke("M14 52L32 14L50 52", 3.5) + stroke("M19.7 40H44.3", 3) +
     dot(32, 14, 5.5) + dot(14, 52, 5, "gold") + dot(50, 52, 5, "tone") + dot(19.7, 40, 3.4, "mist") + dot(44.3, 40, 3.4, "mist"))

mark("Crossbar Foot", "initials", "Monogram",
     "The L's foot keeps going and becomes the A's crossbar, so the two letters lock into one shape.",
     stroke("M12 10V44H48.9", 5) + stroke("M28 56L40 10L52 56", 5))

# II. Atlas ------------------------------------------------------------
mark("Three-Fold Map", "atlas", "Metaphor fusion",
     "A folded map whose three panels are the three kinds of lab: wet, hybrid, dry.",
     f'<path d="M8 16L23 10.5V50L8 55.5Z" {F("gold")}/><path d="M25 10.5L39 16V55.5L25 50Z" {F("mist")}/><path d="M41 16L56 10.5V50L41 55.5Z" {F("tone")}/>')

mark("Dotted Equator", "atlas", "Evolution of current mark",
     "The current icon's three dots, now sitting on a globe's equator. The smallest step from the current icon.",
     f'<circle cx="32" cy="32" r="22" fill="none" stroke="{INK}" stroke-width="4"/>' +
     f'<ellipse cx="32" cy="32" rx="9" ry="22" fill="none" stroke="{INK}" stroke-width="2.2" opacity=".45"/>' +
     stroke("M10 32H54", 2.2, extra='opacity=".45"') + dot(19, 32, 4.6, "gold") + dot(32, 32, 4.6, "mist") + dot(45, 32, 4.6, "tone"))

mark("Banded Globe", "atlas", "Construction",
     "A sphere cut along two latitudes into wet, hybrid and dry bands.",
     '<mask id="@@m"><circle cx="32" cy="32" r="24" fill="#fff"/><path d="M4 24Q32 31 60 24M4 40Q32 47 60 40" stroke="#000" stroke-width="3" fill="none"/></mask>'
     f'<g mask="url(#@@m)"><rect y="0" width="64" height="28" {F("gold")}/><rect y="27" width="64" height="16" {F("mist")}/><rect y="42" width="64" height="22" {F("tone")}/></g>')

cells = "".join(
    f'<rect x="{10+c*16}" y="{10+r*16}" width="12" height="12" rx="2.5" ' +
    (F("gold") if (r, c) == (1, 2) else f'fill="none" stroke="{INK}" stroke-width="2" opacity=".4"') + '/>'
    for r in range(3) for c in range(3))
mark("Grid Reference", "atlas", "Product action",
     "An atlas index grid with one square filled: the lab you were looking for, found.", cells)

mark("Contour Summit", "atlas", "Metaphor fusion",
     "Topographic contour lines rising to a peak, with the peak marked in gold.",
     stroke("M10 50C10 34 22 10 34 10C48 10 56 34 54 50C52 56 12 56 10 50Z", 3.5, "tone") +
     stroke("M18 46C18 34 26 20 34 20C44 20 48 36 46 46C45 50 19 50 18 46Z", 3.5, "mist") +
     stroke("M26 42C26 36 30 30 34 30C40 30 40 38 39 42C38 45 27 45 26 42Z", 3.5, "gold") + dot(34, 37, 2.6))

mark("Needle Drop", "atlas", "Metaphor fusion",
     "A drop and a map pin set point to point make a compass needle: lab work that finds its direction.",
     f'<circle cx="32" cy="32" r="26" fill="none" stroke="{INK}" stroke-width="2.5" opacity=".4"/>'
     f'<g transform="rotate(35 32 32)"><path d="M32 7C37 18 40 26 40 32H24C24 26 27 18 32 7Z" {F("gold")}/>'
     f'<path d="M24 32H40C40 38 37 46 32 57C27 46 24 38 24 32Z" {F("tone")}/></g>' + dot(32, 32, 3.6, extra='') )

route = ((12, 50), (12, 34), (30, 42), (30, 28)); route2 = ((30, 28), (30, 15), (46, 22), (50, 14))
mark("Route", "atlas", "Product action",
     "A dotted route through three stops, ending at a ringed destination.",
     stroke("M12 50C12 34 30 42 30 28C30 15 46 22 50 14", 3, extra='stroke-dasharray="0.1 5.5"') +
     dot(12, 50, 4.5, "gold") + dot(30, 28, 4.5, "mist") + dot(50, 14, 4.5, "tone") +
     f'<circle cx="50" cy="14" r="8.5" fill="none" {S("tone")} stroke-width="2.2"/>')

mark("Cradle", "atlas", "Metaphor fusion",
     "A world held in an open hand, the way Atlas carries it.",
     dot(32, 27, 14, "tone") + stroke("M18.5 27Q32 32 45.5 27", 2.2, "ground") +
     f'<ellipse cx="32" cy="27" rx="6" ry="14" fill="none" {S("ground")} stroke-width="2.2"/>' +
     stroke("M10 32A22 22 0 0 0 54 32", 5))

mark("Tented Atlas", "atlas", "Monogram + meaning",
     "A book left open face down forms an A. Its fanned pages stand for the three kinds of lab.",
     stroke("M32 18Q25 35 19 52", 3, "gold") + stroke("M32 18V53", 3, "mist") + stroke("M32 18Q39 35 45 52", 3, "tone") +
     stroke("M8 52L32 12L56 52", 5))

mark("Map Layers", "atlas", "Construction",
     "Three stacked map layers, like a GIS view, one per kind of lab.",
     stroke("M10 42L32 53L54 42", 4.5, "gold") + stroke("M10 32L32 43L54 32", 4.5, "mist") +
     f'<path d="M32 11L54 22L32 33L10 22Z" {F("tone")} stroke-linejoin="round"/>')

mark("Compass Rose", "atlas", "Construction",
     "A plain four-point rose with only north in gold. It keeps the tradition and drops the ornament.",
     f'<path d="M32 6L37 27L58 32L37 37L32 58L27 37L6 32L27 27Z" fill="{INK}"/>' +
     f'<path d="M32 6L37 27L32 32L27 27Z" {F("gold")}/>' + dot(32, 32, 2.6, "ground"))

mark("Pin Flask", "atlas", "Negative space",
     "A map pin with a flask cut out of it: a place where science happens.",
     '<mask id="@@m"><rect width="64" height="64" fill="#fff"/><path d="M28.5 12H35.5V20L44 35H20L28.5 20Z" fill="#000" stroke="#000" stroke-width="1.5" stroke-linejoin="round"/></mask>'
     f'<path d="M32 59C22 45 11 37 11 24A21 21 0 0 1 53 24C53 37 42 45 32 59Z" fill="{INK}" mask="url(#@@m)"/>' +
     f'<path d="M23.4 29H40.6L44 35H20Z" {F("gold")}/>')

grid = "".join(f'<path d="M{v} 8V48M8 {v}H48" stroke="{INK}" stroke-width="1.4" opacity=".4"/>' for v in (16, 22, 28, 34, 40))
mark("Loupe Grid", "atlas", "Product action",
     "A magnifier over a map grid, with one point in focus. This is what the product does: search.",
     f'<clipPath id="@@c"><circle cx="28" cy="28" r="15"/></clipPath><g clip-path="url(#@@c)">{grid}</g>' +
     dot(31, 25, 3.8, "gold") + f'<circle cx="28" cy="28" r="17" fill="none" stroke="{INK}" stroke-width="5"/>' +
     stroke("M40.5 40.5L54 54", 7))

# III. Lab -------------------------------------------------------------
yc = 40 - math.sqrt(18*18 - 3*3)
mark("Round-Bottom Globe", "lab", "Metaphor fusion",
     "A round-bottom flask is already a globe. The liquid line doubles as the equator, so the mark reads as lab and atlas at once.",
     f'<clipPath id="@@c"><circle cx="32" cy="40" r="16"/></clipPath>'
     f'<g clip-path="url(#@@c)"><path d="M10 41Q32 47 54 41V64H10Z" {F("tone")}/>'
     f'<ellipse cx="32" cy="40" rx="7" ry="18" fill="none" stroke="{INK}" stroke-width="2" opacity=".5"/></g>' +
     stroke(f"M29 8V{yc:.2f}A18 18 0 1 0 35 {yc:.2f}V8", 4.5) + stroke("M25.5 8H38.5", 4.5), pick=True)

mark("Globe Flask", "lab", "Metaphor fusion",
     "An Erlenmeyer flask filled with latitude lines, one per kind of lab.",
     '<clipPath id="@@c"><path d="M29 8V24L13 52Q12 56 16 56H48Q52 56 51 52L35 24V8Z"/></clipPath>'
     f'<g clip-path="url(#@@c)" fill="none" stroke-width="3.2">'
     f'<path d="M4 36Q32 42 60 36" {S("gold")}/><path d="M4 43Q32 49 60 43" {S("mist")}/><path d="M4 50Q32 56 60 50" {S("tone")}/></g>' +
     stroke("M29 8V24L13 52Q12 56 16 56H48Q52 56 51 52L35 24V8M26 8H38", 4.5))

mark("Flask A", "lab", "Monogram + meaning",
     "The A becomes a vessel: liquid fills it up to the crossbar and bubbles rise through the apex.",
     f'<path d="M18.6 40H45.4L51.5 56H12.5Z" {F("gold")}/>' +
     stroke("M12 56L32 8L52 56", 5) + stroke("M18.6 40H45.4", 4.5) +
     f'<circle cx="31" cy="31" r="3" fill="none" {S("mist")} stroke-width="2.2"/><circle cx="34" cy="22" r="2" fill="none" {S("tone")} stroke-width="2"/>')

mark("Petri Contours", "lab", "Metaphor fusion",
     "Rings spreading in a petri dish that also read as a contour map.",
     f'<circle cx="32" cy="32" r="24" fill="none" stroke="{INK}" stroke-width="3.5"/>' +
     f'<circle cx="28.5" cy="34" r="15" fill="none" {S("tone")} stroke-width="3"/>' +
     f'<circle cx="26" cy="36" r="8.5" fill="none" {S("mist")} stroke-width="3"/>' + dot(24.5, 37, 3.4, "gold"))

mark("Petri Colonies", "lab", "Evolution of current mark",
     "Today's three dots become three colonies of different sizes growing in a dish.",
     f'<circle cx="32" cy="32" r="24" fill="none" stroke="{INK}" stroke-width="4"/>' +
     f'<circle cx="32" cy="32" r="19.5" fill="none" stroke="{INK}" stroke-width="1.4" opacity=".35"/>' +
     dot(24, 26, 7, "gold") + dot(40.5, 23.5, 4, "mist") + dot(36, 41, 8.5, "tone"))

tubes = ""
for x, top, c in [(18, 36, "gold"), (32, 28, "mist"), (46, 18, "tone")]:
    tubes += f'<path d="M{x-3} {top}V46A3 3 0 0 0 {x+3} 46V{top}Z" {F(c)}/>'
    tubes += stroke(f"M{x-5} 9V46A5 5 0 0 0 {x+5} 46V9", 3)
mark("Test Tube Trio", "lab", "Product action",
     "Three tubes filled to rising levels. It reads as a rack and as a bar chart.",
     tubes + stroke("M8 22H56", 3, extra='opacity=".6"'))

c1 = ((32, 8), (14, 16), (14, 24), (32, 32)); c2 = ((32, 8), (50, 16), (50, 24), (32, 32))
rungs = ""
for y in (14, 20, 26):
    rungs += stroke(f"M{x_at_y(c1, y)+2.5:.1f} {y}H{x_at_y(c2, y)-2.5:.1f}", 2.2, "mist")
    rungs += stroke(f"M{x_at_y(c1, y)+2.5:.1f} {64-y}H{x_at_y(c2, y)-2.5:.1f}", 2.2, "mist")
mark("Helix Meridians", "lab", "Metaphor fusion",
     "Inside a circle, a double helix doubles as the curved meridians of a globe.",
     f'<circle cx="32" cy="32" r="24" fill="none" stroke="{INK}" stroke-width="3.5"/>' + rungs +
     stroke("M32 8C14 16 14 24 32 32C50 40 50 48 32 56", 3.5, "gold") +
     stroke("M32 8C50 16 50 24 32 32C14 40 14 48 32 56", 3.5, "tone"))

px = ""
for x, y, c in [(20, 47, "gold"), (26, 47, "gold"), (32, 47, "mist"), (38, 47, "tone"), (26, 41, "gold"), (32, 41, "mist"), (38, 41, "tone"), (32, 35, "tone")]:
    px += f'<rect x="{x-2.4}" y="{y-2.4}" width="4.8" height="4.8" rx="1" {F(c)}/>'
mark("Pixel Flask", "lab", "Metaphor fusion",
     "A flask filled with pixels instead of liquid: the bench and the computer in one vessel.",
     px + dot(36, 28, 1.8, "tone") + stroke("M29 8V24L13 52Q12 56 16 56H48Q52 56 51 52L35 24V8M26 8H38", 4.5))

mark("Drop on the Map", "lab", "Product action",
     "A pipette lets one drop fall onto a map line. This is where the experiment happens.",
     f'<ellipse cx="32" cy="11" rx="6" ry="6.5" fill="{INK}"/>' + stroke("M30 18V32L32 37L34 32V18Z", 2.8) +
     f'<path d="M32 40C32 40 26.5 46.5 26.5 50a5.5 5.5 0 0 0 11 0C37.5 46.5 32 40 32 40Z" {F("gold")}/>' +
     stroke("M8 58H24M40 58H56", 2.6, extra='opacity=".5"'))

mark("Beaker Bars", "lab", "Metaphor fusion",
     "A beaker holding a bar chart: wet-lab glass, dry-lab data.",
     f'<rect x="20" y="37" width="6" height="13" rx="1" {F("gold")}/><rect x="29" y="29" width="6" height="21" rx="1" {F("mist")}/><rect x="38" y="20" width="6" height="30" rx="1" {F("tone")}/>' +
     stroke("M10 9H14V50Q14 55 19 55H45Q50 55 50 50V9H54", 4.5))

mark("Iso Cube", "lab", "Construction",
     "An isometric cube with one face per kind of lab: a single solid block of research.",
     '<mask id="@@m"><rect width="64" height="64" fill="#fff"/><path d="M32 32.5L13 21.5M32 32.5L51 21.5M32 32.5V55" stroke="#000" stroke-width="2.4"/></mask>'
     f'<g mask="url(#@@m)"><path d="M32 10L51 21V43L32 54L13 43V21Z" {F("tone")}/><path d="M32 10L51 21L32 32L13 21Z" {F("mist")}/><path d="M13 21L32 32V54L13 43Z" {F("gold")}/></g>')

hexv = [(32+20*math.cos(math.radians(a)), 32+20*math.sin(math.radians(a))) for a in range(-90, 270, 60)]
hexd = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in hexv) + "Z"
mark("Ring Nodes", "lab", "Construction",
     "A benzene ring with a coloured atom at every other corner. Chemistry's most familiar shape, made specific to the product.",
     stroke(hexd, 4) + f'<circle cx="32" cy="32" r="10.5" fill="none" stroke="{INK}" stroke-width="2.5" opacity=".5"/>' +
     dot(*hexv[0], 5, "gold") + dot(*hexv[2], 5, "mist") + dot(*hexv[4], 5, "tone"))

# IV. Spectrum ---------------------------------------------------------
mark("Wet ∩ Dry", "spectrum", "Product meaning",
     "Wet and dry labs as two circles. Their overlap is cut out, and that gap is the hybrid lab. This is the product's taxonomy as a Venn diagram.",
     dot(23, 32, 16, "gold") + dot(41, 32, 16, "tone") +
     f'<path d="M32 18.75A16 16 0 0 1 32 45.25A16 16 0 0 1 32 18.75Z" {F("ground")}/>', pick=True)

bp = ""
for r in range(3):
    for c, (col, rx) in enumerate([("gold", 6), ("mist", 3.2), ("tone", 0.8)]):
        bp += f'<rect x="{10+c*16}" y="{10+r*16}" width="12" height="12" rx="{rx}" {F(col)}/>'
mark("Bubbles to Pixels", "spectrum", "Product meaning",
     "From left to right, drops turn into pixels. The shift from bench to computer, shown as a change in shape.", bp, pick=True)

mark("Three Primitives", "spectrum", "Construction",
     "Peak, drop and pixel stand for the field, the bench and the computer. Three basic shapes, no letters needed.",
     f'<path d="M30 8L44 32H16Z" fill="{INK}" stroke-linejoin="round"/>' + dot(19, 44, 11, "gold") +
     f'<rect x="33" y="34" width="21" height="21" rx="1.5" {F("tone")}/>')

segs = [("gold", 22), ("ink", 10), ("tone", 44), ("mist", 24)]
ring, off = "", 0
for c, v in segs:
    ring += f'<circle cx="32" cy="32" r="19" fill="none" {S(c)} stroke-width="10" pathLength="100" stroke-dasharray="{v-2.5} {100-v+2.5}" stroke-dashoffset="{-off:.2f}" transform="rotate(-90 32 32)"/>'
    off += v
mark("Census Ring", "spectrum", "Product meaning",
     "The site's wet / hybrid / dry / unplaced bar bent into a ring, so it reads as a globe and as a chart. Proportions are illustrative.",
     ring, pick=True)

arc = ((10, 40), (32, 20), (54, 40))
ad = "".join(dot(*qbez(*arc, t), 5, c) for t, c in [(0.18, "gold"), (0.5, "mist"), (0.82, "tone")])
mark("Arc of Dots", "spectrum", "Evolution of current mark",
     "The current three dots moved onto a curved line of latitude: a globe suggested by a single arc.",
     f'<circle cx="32" cy="38" r="24" fill="none" stroke="{INK}" stroke-width="3" opacity=".25"/>' +
     stroke("M10 40Q32 20 54 40", 2.4, extra='opacity=".6"') + ad)

import random
rnd = random.Random(7)
sc = ""
for _ in range(26):
    while True:
        x, y = rnd.uniform(9, 55), rnd.uniform(9, 55)
        if math.hypot(x-38, y-26) > 11: break
    sc += dot(x, y, 1.7, extra='opacity=".5"')
mark("Found", "spectrum", "Product action",
     "A scatter of investigators with one of them ringed. It says the product's job: find the one lab that fits.",
     sc + dot(38, 26, 3.8, "gold") + f'<circle cx="38" cy="26" r="8.5" fill="none" stroke="{INK}" stroke-width="2.5"/>')

mark("Socket", "spectrum", "Negative space",
     "A circle sitting in a matching notch. The product's promise is fit, so the mark shows a fit.",
     '<mask id="@@m"><rect width="64" height="64" fill="#fff"/><circle cx="43" cy="21" r="12" fill="#000"/></mask>'
     f'<rect x="9" y="9" width="46" height="46" rx="7" fill="{INK}" mask="url(#@@m)"/>' + dot(43, 21, 8.5, "gold"))

pix = ""
for cx in (36, 44, 52):
    for cy in range(12, 56, 8):
        if math.hypot(cx-32, cy-32) <= 25:
            pix += f'<rect x="{cx-3.4}" y="{cy-3.4}" width="6.8" height="6.8" rx="1" {F("tone")}/>'
mark("Analog / Digital", "spectrum", "Product meaning",
     "One sphere: the left half is smooth like a drop, the right half is stepped like a screen.",
     f'<path d="M31 8A24 24 0 0 0 31 56Z" {F("gold")}/>' + pix)

bars = ""
for x, h, c in [(8, 14, "gold"), (19, 28, "gold"), (30, 42, "mist"), (41, 28, "tone"), (52, 14, "tone")]:
    bars += f'<rect x="{x-4}" y="{54-h}" width="8" height="{h}" rx="1.5" {F(c)}/>'
mark("Peak Bars", "spectrum", "Monogram + meaning",
     "A histogram shaped like an A, with a gap cut across it where the crossbar would be.",
     '<mask id="@@m"><rect width="64" height="64" fill="#fff"/><path d="M0 38H64" stroke="#000" stroke-width="3.5"/></mask>'
     f'<g mask="url(#@@m)" transform="translate(4 0)">{bars}</g>')

mark("Prism A", "spectrum", "Metaphor fusion",
     "White light enters an A-shaped prism and leaves split into three beams, one per kind of lab. The beam inside the prism is the crossbar.",
     stroke("M3 39L20 34", 3.2) + stroke("M20 34L40 26", 3.2) +
     stroke("M40 26L61 19", 3.2, "gold") + stroke("M40 26L61 27", 3.2, "mist") + stroke("M40 26L61 35", 3.2, "tone") +
     stroke("M32 9L52 50H12Z", 4.2), pick=True)

arcs = ""
for i, c in enumerate(["gold", "mist", "tone"]):
    a0, a1 = math.radians(-90 + i*120 + 8), math.radians(-90 + i*120 + 112)
    p0 = (32+21*math.cos(a0), 32+21*math.sin(a0)); p1 = (32+21*math.cos(a1), 32+21*math.sin(a1))
    arcs += stroke(f"M{p0[0]:.2f} {p0[1]:.2f}A21 21 0 0 1 {p1[0]:.2f} {p1[1]:.2f}", 4, c)
mark("Ring Seal", "spectrum", "Construction",
     "A seal: a three-part ring around a single-line A. Works on a stamp, a badge or an avatar.",
     f'<circle cx="32" cy="32" r="27" fill="none" stroke="{INK}" stroke-width="1.8" opacity=".5"/>' + arcs +
     stroke("M23 43L32 20L41 43M26 36H38", 4))

mark("Reticle", "spectrum", "Product action",
     "A crosshair locked on a single point: the moment the search lands on the right lab.",
     f'<circle cx="32" cy="32" r="17" fill="none" stroke="{INK}" stroke-width="3.5"/>' +
     stroke("M32 4V14M32 50V60M4 32H14M50 32H60", 3.5) + dot(32, 32, 4.5, "gold"))

mark("Chevron Peak", "spectrum", "Monogram + meaning",
     "Three stacked chevrons, one per kind of lab, climbing like contour lines toward an A.",
     stroke("M12 30L32 12L52 30", 5.5, "gold") + stroke("M12 42L32 24L52 42", 5.5, "mist") + stroke("M12 54L32 36L52 54", 5.5, "tone"))

assert len(M) == 50, len(M)

# ---------------------------------------------------------------- output
def svg_inline(m, size, suffix):
    body = m["svg"].replace("@@", f"k{m['n']}{suffix}")
    return f'<svg viewBox="0 0 64 64" width="{size}" height="{size}" aria-hidden="true">{body}</svg>'

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("∩", "and")).strip("-")

def export_svgs():
    out = os.path.join(HERE, "svg"); os.makedirs(out, exist_ok=True)
    g = GROUNDS["navy"]
    for m in M:
        body = m["svg"].replace("@@", "k")
        body = body.replace("currentColor", g["ink"])
        body = re.sub(r'style="(fill|stroke):var\(--(\w+)\)"', lambda r: f'{r.group(1)}="{g[r.group(2)]}"', body)
        title = html.escape(f"Lab Atlas mark {m['n']:02d}: {m['name']}")
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="256" height="256">'
               f'<title>{title}</title><rect width="64" height="64" rx="14" fill="{g["bg"]}"/>'
               f'<g transform="translate(9.6 9.6) scale(.7)">{body}</g></svg>\n')
        with open(os.path.join(out, f"{m['n']:02d}-{slug(m['name'])}.svg"), "w") as f:
            f.write(doc)

GROUPS = [("initials", "Initials", "L and A built into one symbol"),
          ("atlas", "Atlas", "maps, globes, wayfinding"),
          ("lab", "Lab", "glassware, chemistry, biology"),
          ("spectrum", "Spectrum", "wet, hybrid and dry, and finding a fit")]

def page(fonts_css, full_doc):
    cards = []
    for m in M:
        cards.append(f'''<article class="card" data-group="{m['group']}"{' data-pick' if m['pick'] else ''}>
  <div class="tile">{svg_inline(m, 64, 'a')}{'<span class="pick">Shortlist</span>' if m['pick'] else ''}</div>
  <div class="meta">
    <div class="row"><span class="no">{m['n']:02d}</span><h3>{html.escape(m['name'])}</h3></div>
    <p class="why">{html.escape(m['why'])}</p>
    <div class="row foot"><span class="method">{html.escape(m['method'])}</span>
      <span class="sizes" title="Shown at 32 and 16 pixels"><span class="chip c32">{svg_inline(m, 22, 'b')}</span><span class="chip c16">{svg_inline(m, 11, 'c')}</span></span></div>
  </div>
</article>''')
    sections = []
    for key, label, sub in GROUPS:
        n = sum(1 for m in M if m['group'] == key)
        body = "\n".join(c for c, m in zip(cards, M) if m['group'] == key)
        sections.append(f'<section class="grp" data-section="{key}"><header class="gh"><h2>{label}</h2><span>{sub} · {n}</span></header><div class="grid">{body}</div></section>')
    css = CSS
    head = f'<title>Lab Atlas Marks</title>\n<style>\n{fonts_css}\n{css}\n</style>'
    body = BODY.replace("{{SECTIONS}}", "\n".join(sections)).replace("{{PICKS}}", str(sum(m['pick'] for m in M)))
    if full_doc:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
    return f'{head}\n{body}\n'

CSS = r"""
/* Layout: specimen sheet. A short brief, a sticky filter bar, then four families of square tiles. */
:root{
  --navy:#031b36; --cream:#fdffee;
  --bg:#f3f5ef; --surface:#ffffff; --fg:#031b36; --fg2:#4a5f78; --rule:#d8ddd3; --accent:#0079a8;
  --sans:'Atlas Text',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#020f21;--surface:#0a2544;--fg:#eceae3;--fg2:#a3adb3;--rule:#1d3a5e;--accent:#d4a72c;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#020f21;--surface:#0a2544;--fg:#eceae3;--fg2:#a3adb3;--rule:#1d3a5e;--accent:#d4a72c;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1240px;margin:0 auto;padding-inline:clamp(16px,4vw,40px);padding-block:48px 72px}
.intro{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:40px;align-items:end;padding-bottom:32px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--fg2);margin:0 0 12px}
h1{font-weight:300;font-size:clamp(34px,5vw,60px);line-height:1.02;letter-spacing:-.02em;margin:0;text-wrap:balance}
.lede{color:var(--fg2);max-width:58ch;margin:0}
.lede strong{color:var(--fg);font-weight:500}
.palette{display:flex;gap:6px;margin-top:16px;flex-wrap:wrap}
.palette span{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--fg2)}
.palette i{width:12px;height:12px;border-radius:50%;display:inline-block}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center;justify-content:space-between;padding-block:14px;border-bottom:1px solid var(--rule)}
.seg{display:flex;flex-wrap:wrap;gap:6px}
.seg button{font:inherit;font-size:13px;color:var(--fg);background:transparent;border:1px solid var(--rule);border-radius:999px;padding:6px 12px;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.seg button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.seg .lbl{font-size:12px;color:var(--fg2);align-self:center;margin-right:4px;letter-spacing:.06em;text-transform:uppercase}
.grp{padding-top:36px}
.gh{display:flex;align-items:baseline;gap:14px;margin-bottom:16px}
.gh h2{font-weight:400;font-size:24px;margin:0;letter-spacing:-.01em}
.gh span{color:var(--fg2);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;min-width:0}
.tile{--ink:var(--cream);--gold:#d4a72c;--tone:#9ea8a8;--mist:#5a6b76;--ground:var(--navy);
  background:var(--navy);color:var(--ink);aspect-ratio:1/1;max-width:100%;display:grid;place-items:center;position:relative}
.tile svg{width:52%;height:52%}
main[data-ground="paper"] .tile, main[data-ground="paper"] .chip{--ink:var(--navy);--gold:#b98a12;--tone:#62727c;--mist:#a6afae;--ground:var(--cream);background:var(--cream);color:var(--ink)}
main[data-ground="paper"] .tile{box-shadow:inset 0 -1px 0 var(--rule)}
.pick{position:absolute;top:10px;left:10px;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--navy);background:#d4a72c;border-radius:999px;padding:2px 8px}
.meta{padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px;flex:1}
.row{display:flex;align-items:baseline;gap:10px}
.no{font-variant-numeric:tabular-nums;color:var(--fg2);font-size:13px}
.card h3{margin:0;font-size:16px;font-weight:500}
.why{margin:0;color:var(--fg2);font-size:13.5px;line-height:1.45;flex:1}
.foot{justify-content:space-between;align-items:center}
.method{font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--fg2)}
.sizes{display:flex;gap:6px;align-items:center}
.chip{--ink:var(--cream);--gold:#d4a72c;--tone:#9ea8a8;--mist:#5a6b76;--ground:var(--navy);background:var(--navy);color:var(--ink);display:grid;place-items:center;border-radius:7px}
.chip.c32{width:32px;height:32px}.chip.c16{width:16px;height:16px;border-radius:4px}
.chip.c16 svg{width:14px;height:14px}
.card[hidden],.grp[hidden]{display:none!important}
.notes{margin-top:56px;padding-top:28px;border-top:1px solid var(--rule);display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:28px}
.notes h4{margin:0 0 6px;font-weight:500;font-size:15px}
.notes p{margin:0;color:var(--fg2);font-size:14px;max-width:60ch}
@media (max-width:760px){.intro{grid-template-columns:minmax(0,1fr);gap:20px}.grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}.why{font-size:13px}}
@media (prefers-reduced-motion:no-preference){.card{transition:transform .25s cubic-bezier(.16,1,.3,1)}.card:hover{transform:translateY(-2px)}}
"""

BODY = r"""<div class="wrap">
  <div class="intro">
    <div>
      <p class="eyebrow">Lab Atlas · identity exploration</p>
      <h1>Fifty marks, no words.</h1>
    </div>
    <div>
      <p class="lede">Each concept is a single symbol for Lab Atlas, the directory that shows whether a research lab works at the bench, at a computer or both. Every mark is built on a 64-unit grid in <strong>one ink colour and one gold accent</strong>, with two softer tones of the ink where a mark needs more than one shade. Nothing is tied to one university.</p>
      <div class="palette" aria-hidden="true"><span><i style="background:#d4a72c"></i>Gold</span><span><i style="background:#fdffee;box-shadow:inset 0 0 0 1px #8b98a6"></i>Cream</span><span><i style="background:#9ea8a8"></i>Tone</span><span><i style="background:#5a6b76"></i>Mist</span><span><i style="background:#031b36;box-shadow:inset 0 0 0 1px #5d7088"></i>Navy</span></div>
    </div>
  </div>
  <div class="bar">
    <div class="seg" role="group" aria-label="Filter concepts">
      <button type="button" id="f-all" data-filter="all" aria-pressed="true">All 50</button>
      <button type="button" id="f-pick" data-filter="pick" aria-pressed="false">Shortlist · {{PICKS}}</button>
      <button type="button" id="f-initials" data-filter="initials" aria-pressed="false">Initials</button>
      <button type="button" id="f-atlas" data-filter="atlas" aria-pressed="false">Atlas</button>
      <button type="button" id="f-lab" data-filter="lab" aria-pressed="false">Lab</button>
      <button type="button" id="f-spectrum" data-filter="spectrum" aria-pressed="false">Spectrum</button>
    </div>
    <div class="seg" role="group" aria-label="Background">
      <span class="lbl">Ground</span>
      <button type="button" id="g-navy" data-ground="navy" aria-pressed="true">Navy</button>
      <button type="button" id="g-paper" data-ground="paper" aria-pressed="false">Paper</button>
    </div>
  </div>
  <main id="sheet" data-ground="navy">
{{SECTIONS}}
  </main>
  <div class="notes">
    <div><h4>How they were made</h4><p>Five methods from the workspace's brand-kit guidance: monogram plus meaning, product action, metaphor fusion, negative space and construction geometry. No mark uses more than two ideas at once.</p></div>
    <div><h4>Small-size check</h4><p>The two chips on each card show the mark at 32 and 16 pixels, the sizes for an app icon and a browser tab. A mark that falls apart at 16 needs a simpler favicon version.</p></div>
    <div><h4>The shortlist</h4><p>The seven gold-tagged marks carry the most meaning in the fewest strokes. Round-Bottom Globe and Prism A each read as both lab and atlas. Wet ∩ Dry and Bubbles to Pixels draw the product's own categories.</p></div>
  </div>
</div>
<script>
(function(){
  var sheet=document.getElementById('sheet');
  var fb=[].slice.call(document.querySelectorAll('[data-filter]'));
  var gb=[].slice.call(document.querySelectorAll('[data-ground]')).filter(function(b){return b.tagName==='BUTTON'});
  function store(k,v){try{localStorage.setItem(k,v)}catch(e){}}
  function read(k){try{return localStorage.getItem(k)}catch(e){return null}}
  function filter(f){
    fb.forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.filter===f))});
    document.querySelectorAll('.grp').forEach(function(s){
      var any=false;
      s.querySelectorAll('.card').forEach(function(c){
        var show=f==='all'||(f==='pick'?c.hasAttribute('data-pick'):c.dataset.group===f);
        c.hidden=!show; if(show)any=true;
      });
      s.hidden=!any;
    });
    store('la-filter',f);
  }
  function ground(g){
    sheet.dataset.ground=g;
    gb.forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.ground===g))});
    store('la-ground',g);
  }
  fb.forEach(function(b){b.addEventListener('click',function(){filter(b.dataset.filter)})});
  gb.forEach(function(b){b.addEventListener('click',function(){ground(b.dataset.ground)})});
  var f=read('la-filter'),g=read('la-ground');
  if(f&&document.querySelector('[data-filter="'+f+'"]'))filter(f);
  if(g==='paper'||g==='navy')ground(g);
})();
</script>"""

if __name__ == "__main__":
    fonts = ""
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        fonts = open(sys.argv[1]).read()
    export_svgs()
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page(fonts, True))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            f.write(page(fonts, False))
    print("built", len(M), "marks")
