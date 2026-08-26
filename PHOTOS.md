# Adding photographs to the Lab Atlas

Every image on the page is declared in one place: the `PHOTOS` object near the
top of the `<script>` block in `Emory_Lab_Atlas_v52.html`. Search the file for
`================= PHOTOGRAPHY =================`.

Nothing else needs editing. The slots, sizing, treatment, lazy loading and
fallbacks are already built.

## The two placements

| Slot | Size | Subject |
|---|---|---|
| `opening` | 1400 x 1120 (5:4) | one campus or architecture frame, shown beside the headline above the network |
| `unit.<KEY>` | 320 x 240 (4:3) | the building or institute, one per school row |

The nine unit keys are fixed and must not be renamed:

`SOM` `CHOA` `Winship` `RSPH` `Nursing` `ECAS` `EPC` `Vaccine` `ECCRI`

## Adding one

```
base64 -w0 som.jpg
```

Paste the output as the value, with the data-URI prefix:

```js
SOM: 'data:image/jpeg;base64,/9j/4AAQSkZJRg...',
```

A plain URL (`'https://.../som.jpg'`) also works, but the rest of this file is
deliberately self-contained — the typeface and the Emory shield are both
embedded — so a URL is the one thing in it that breaks on a machine with no
network. Prefer the data URI.

Optionally set `openingCredit` to a short line printed over the opening
photograph, e.g. `'Emory University, Atlanta'`.

## A partial set is fine

Leave a slot as `''` and that row prints its own key on a ground taken from the
institute's colour. That is a designed state, not a broken one, so you can fill
in the schools you have and add the rest later.

## What the page does to a photograph

Nine buildings shot on nine different days will fight each other and the
wet/dry palette if dropped in raw, so every image is passed through the same
treatment: saturation pulled down, contrast lifted slightly, and a tint toward
the ground colour of the current theme. Pointing at an image returns it to full
colour. Dark mode dims it further. None of this needs configuring.

## Before you source images

Photographs sitting beside 7,096 named investigators imply those are their
buildings. Use real Emory photography the university has rights to. Generic
stock images of laboratories would misrepresent the records and would read as
less credible, not more.

Faculty headshots are a separate decision: they need ~7,000 images plus
licensing and privacy clearance from Emory, and there is no slot for them yet.
