# Human check of the wet/dry labels

The model's accuracy (91.6% on the locked test set) is measured against gold
labels that **Claude** assigned by reading each record under
`../LABELLING_RUBRIC.md`. That shows the model agrees with one careful,
consistent reader. It does not show that reader is right. This folder is the
check: people who know Emory's labs label a random sample of the same test
set themselves, blind, and the labels are compared.

## Files

| file | what it is | who sees it |
|---|---|---|
| `labelling_sheet.xlsx` | the workbook to fill in: Instructions, Label (one row per person, yellow cells to fill), Records (each person's full record: units, profile text, grants, every title), Progress (live counts) | the labellers |
| `key.csv` | maps the sheet's codes (H001-H150) to atlas records | **not** the labellers |

The sheet holds only what is on each record. It contains no model output and
none of Claude's labels, so it can be labelled blind. The 150 people are a
random draw (seed 20260926) from the 400-person locked test set, in random
order. `make_human_check.py` rebuilds exactly the same workbook.

## Running the check

1. **Choose one or two labellers** who know biomedical research at Emory: a
   faculty member, a senior postdoc, a graduate programme coordinator. Two
   people give an extra number: how often two humans agree, which says how
   hard the call really is.
2. **Give each person their own copy** of `labelling_sheet.xlsx`. Ask them to
   work alone and not open the atlas or this repository until they are done.
   Allow about 2 minutes per person, so roughly 5 hours for all 150. A partly
   filled sheet can still be scored.
3. **Ask for the file back** saved as `labelling_sheet_<initials>.xlsx`.
4. **Score it:**

   ```sh
   python3 ml/human_check.py labelling_sheet_JS.xlsx labelling_sheet_AK.xlsx --out ml/human_check/results
   ```

   This writes `results.md`, `disagreements.csv` and `human_labels.csv`.

## Reading the results

- **Agreement with Claude's labels, and kappa.** How far the answer key can be
  trusted. As a rough guide for a four-way label: kappa above 0.8 is strong,
  0.6-0.8 good, below 0.6 means the key needs work. The "wet vs not wet" row
  matters most, because that is what the atlas's filter uses.
- **The model, judged by these labels vs by Claude's, on the same people.** If
  the interval of the difference contains zero, the published accuracy stands
  on human labels. If it sits below zero, the page overstates accuracy by about
  that much, and the answer key should be corrected.
- **After web check.** The first label is judged from the record alone, the
  same evidence Claude and the model had. The optional second label says what
  the person believes once they know the lab. A gap between the two points at
  the scrape (missing or misattributed papers) rather than at the reading.
- **Between people.** If two people agree with each other much more than with
  Claude, Claude's reading is off. If they disagree with each other as often as
  with Claude, the rubric leaves too much to judgment, most likely on hybrids.

## Acting on it

Go through `disagreements.csv` together: every label and note is side by side
with Claude's and the model's. Where the people are right, edit that row of
`ml/gold_labels.csv`:
- set `label` and `conf`;
- add a note such as `corrected by human check (JS, AK)`.

Then rebuild with `scripts/build_atlas.sh`. The model retrains on the corrected
labels, and every figure on the page is re-measured.

## Limits

- 150 is enough to measure agreement to within about ±5 points.
- It is not enough for hybrids: about 5 are expected in the sample.
- To check hybrids specifically, a second, targeted sheet would be needed.
