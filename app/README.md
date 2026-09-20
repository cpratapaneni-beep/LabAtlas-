# Emory Lab Atlas: landing + atlas

The landing page is a Vite/React app. The atlas is the single self-contained
HTML file at the repository root, which the landing opens in a panel.

## Setup

```
pnpm install
mkdir -p client/public/atlas
cp ../Emory_Lab_Atlas_v62.html client/public/atlas/index.html
pnpm dev
```

The atlas file is about 43MB and lives at the root rather than being committed
a second time inside `client/public`, which is why that path is gitignored and
the copy is a setup step.

## How the two fit together

The landing never navigates away. Every way in (the nav button, the hero
buttons, both floating hero cards, all three station cards, the teaser window,
and "Read the notes") calls one `openAtlas(view, event)`. That measures the
element that was clicked and grows a panel out of its rectangle to full screen,
so the atlas arrives from the thing you pressed.

Only `transform` and `opacity` are animated. The panel is always full size and
is scaled down to the source rectangle, then released, so nothing reflows while
it moves. Under `prefers-reduced-motion` it opens at full size with no growth.

Each entry point names the view it lands on, passed as a URL fragment:

| Entry point                                | Lands on  |
| ------------------------------------------ | --------- |
| Nav, hero, teaser window                    | `#atlas`  |
| "Find your people"                          | `#find`   |
| "Follow the links", first-degree ties card  | `#graph`  |
| "Read the notes"                            | `#notes`  |

The atlas reads and writes that fragment itself, so a reload or a shared link
keeps its place, and it also accepts a `postMessage` of
`{type:"atlas:view", view:"graph"}`.

When the atlas detects it is inside a frame it defers its arrival note until
the transition has finished, and drops its own wordmark, since the panel
already names the product and carries the way out.

## Design

The landing uses the atlas's tokens rather than its own: the navy ground and
ink ramp, the wet/hybrid/dry colours, the gold accent, 2px corners, and Inter
embedded from the atlas's own three faces. Crossing between the two should not
read as crossing between two products.
