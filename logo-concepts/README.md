# Lab Atlas: logo concepts

50 single-symbol marks for Lab Atlas. None uses words, and none is tied to a single university.

- `index.html`: the gallery. Open it in a browser to filter by family, see the shortlist, and switch between navy and paper backgrounds.
- `svg/`: each mark as a standalone 256px SVG on a navy app-icon tile.
- `build.py`: generates both of the above. Every mark is defined there on a 64-unit grid.

Rebuild: `python3 build.py [atlas-text.css]`. The optional argument is a CSS file of `@font-face` rules for the product's Atlas Text font. Without it, the gallery uses the system sans-serif.

Colours: cream `#fdffee` ink and gold `#d4a72c` accent on navy `#031b36`, with two neutral tones of the ink (`#9ea8a8`, `#5a6b76`). The earlier blue/pink/red scheme has been removed.

Shortlist: 02 Axes & Peak, 04 Pole A, 26 Round-Bottom Globe, 38 Wet ∩ Dry, 39 Bubbles to Pixels, 41 Census Ring, 47 Prism A.

## Round two: emblems

`emblems/` holds 24 more detailed emblems in an engraved-atlas and seal style: hatching, stipple, graduated rims, laurels, stars.

- Each emblem comes in two sample palettes: **Navy & gold** (navy, gold, cream) and **Earth** (sepia ink on parchment, with ochre, sage and burnt sienna).
- Each emblem also has a simplified small version for favicons and app icons.
- `emblems/index.html` is the gallery. `emblems/svg/` holds four files per emblem: full and small, in each palette.
- Rebuild with `python3 emblems/build.py [atlas-text.css]`.

## Round three: Pole A

`pole-a/` develops concept 04 (Pole A) from the first round. The A is two meridians meeting at the north pole, with a parallel as its crossbar. The L is built from the same globe, and the background is a true orthographic globe (`pole-a/globe.py`).

- The lead version, Graticule Ligature, draws both letters as lines of the globe's 15° grid in one unbroken stroke.
- There are eight variations, each in the navy-and-gold and earth palettes, with a simplified small version.
- Rebuild with `python3 pole-a/build.py [atlas-text.css]`.

## Round four: the atlas moth

`moth/` combines the atlas moth with the Pole A globe in six ways: perched on the pole, an L and an A cut as windows in map-gridded wings, a seal, flying toward the globe, hemisphere wings that spell LA, and a resting moth shaped like an A on an L-shaped branch. It reuses the `pole-a` geometry. Rebuild with `python3 moth/build.py [atlas-text.css]`.

In `pole-a/`, the L is now nearly as tall as the A: it comes down the 82°W meridian from 72°N, and the view is rotated to 22°W so the L stays straight.

## Rounds five and six: drawn to the light, then silhouette

- `drawn-to-the-light/` redraws the moth in side view, flying, with no face and no letters on its wings, and places it in front of the glowing Pole A globe.
- `silhouette/` is the chosen direction. The moth is a single dark shape crossing the lit globe, framed by a compass ring with graduated ticks and half-shaded cardinal pointers instead of light rays. North carries a star.
- The silhouette round has six versions: lead, plain globe, rose behind, breaking the ring, one colour, and night globe.
- Rebuild with `python3 silhouette/build.py [atlas-text.css]`.

## Round seven: the titan Atlas

`atlas-titan/` drops the moth and models the mark on the titan Atlas carrying the heavens. He is a dark silhouette on the lit disc inside the compass ring, and the sphere he carries has the globe grid and Pole A cut into it, as on a black-figure vase.

- The poses are drawn in `atlas-titan/figure.py`: the Farnese kneeling pose, a standing pose whose legs form an A, and a shoulders-and-sphere bust for small sizes.
- There are six versions: Farnese Atlas, Standing Titan, Black-figure Vase (Greek key border), Titan's Shoulders, Night Titan and One Colour.
- Rebuild with `python3 atlas-titan/build.py [atlas-text.css]`.

## Round eight: YC Fall 2026 conventions

`yc-style/` starts over from a review of all 127 logos in the YC Fall 2026 batch, taken from the public YC directory. The patterns: a single heavy flat glyph on black or white, letters cut from geometry, at most one accent colour, and pixel and stencil marks.

- The round has fifteen marks on a 100-unit grid: Pole A, Knockout Globe, Bitmap Globe, North Star A, LA Blocks, One Stroke, Titan, Pin A, Graticule Cell, Compass, Lens, Folded Map, Latitude Bars, Pole Star and Meridian Point.
- The gallery shows each mark on black, white and navy, with an accent switch: signal orange, gold or none.
- Rebuild with `python3 yc-style/build.py [atlas-text.css]`.

## Round nine (paused): circle-and-ellipse marques

`emblem-marques/` holds emblems built only from circles and ellipses, after Audi and Toyota: Horizon, Atlas Arch, Orbit A, Armillary and Borromean. Each is rendered flat, as a chrome badge and as a construction drawing. It is paused while the product name is reconsidered: labatlas.com belongs to an existing research-lab product. Rebuild with `python3 emblem-marques/build.py [atlas-text.css]`.

## Benchcarta

The product is now called **Benchcarta**: bench + carta (Latin and Italian for map). labatlas.com belongs to an existing research-lab product. benchcarta.com and benchcarta.io were unregistered when checked.

`benchcarta/` has seven marks built only from circles, ellipses and straight lines: Hemisphere B, Linked bc, Bench Globe, Compass C, Contour C, Pin C and Open Globe. Each is shown flat, in chrome, as a construction drawing and in a lockup with the name. It reuses the renderers from `emblem-marques/`. Rebuild with `python3 benchcarta/build.py [atlas-text.css]`.

### Benchcarta, round two: Open Globe turned

`benchcarta/open_globe.py` turns the Open Globe 90° to the left, so the opening and its point face the top and the globe reads as a round-bottom flask. There are four versions, each with a science reference: Flask Globe (a narrowed opening with a neck and lip), Rising Bubbles, Molecule (a benzene hexagon) and Atom Globe (two electron orbits). The page is `benchcarta/open-globe.html` and the SVGs are in `benchcarta/svg-open-globe/`.

### Benchcarta, round three: Atom Globe

`benchcarta/atom.py` closes the circle and removes the rising line, leaving a globe that holds two electron orbits around a nucleus. It adds one map reference that leaves the circle whole, in four versions: North Pointer, Compass Ticks, Pin Nucleus and Compass Bezel. The page is `benchcarta/atom.html` and the SVGs are in `benchcarta/svg-atom/`.
