# Lab Atlas: logo concepts

50 single-symbol marks for Lab Atlas. None uses words, and none is tied to a single university.

- `index.html`: the gallery. Open it in a browser to filter by family, see the shortlist, and switch between navy and paper backgrounds.
- `svg/`: each mark as a standalone 256px SVG on a navy app-icon tile.
- `build.py`: generates both of the above. Every mark is defined there on a 64-unit grid.

Rebuild: `python3 build.py [atlas-text.css]`. The optional argument is a CSS file of `@font-face` rules for the product's Atlas Text font. Without it, the gallery uses the system sans-serif.

Colours: coral `#cf5f49` (wet), lilac `#c9a2f2` (hybrid), blue `#3b8ccc` (dry), gold `#d4a72c` (highlight), on navy `#031b36` with cream `#fdffee` ink.

Shortlist: 02 Axes & Peak, 04 Pole A, 26 Round-Bottom Globe, 38 Wet ∩ Dry, 39 Bubbles to Pixels, 41 Census Ring, 47 Prism A.
