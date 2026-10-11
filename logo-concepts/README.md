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
