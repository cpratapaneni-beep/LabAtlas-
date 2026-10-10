# Review of the first human check (Labeller 1, October 2026)

One person labelled all 150 people in `labelling_sheet_L1.xlsx` blind, marked
135 of them sure, wrote notes on 52, and gave an after-web-check label for
every row. `results.md` is the scorer's report; this file is the reading of it.

## The numbers

| | result |
|---|---|
| Same label as Claude (W/D/H/U) | 82.7% (kappa 0.51) |
| Wet vs not wet, same as Claude | 94.0% (kappa 0.75) |
| Model on the right side, by Labeller 1 | 81.1% (74.5-87.2%) |
| Model on the right side, by Claude, same 150 | 92.7% (87.9-96.6%) |
| Where both could judge (no U on either side, 136 people): model by Labeller 1 / by Claude | 86.8% / 92.6% |

The four-way kappa of 0.51 sits below the 0.6 line the README gives for
"the key needs work". The wet-vs-not-wet agreement, which is what the atlas
filter uses, is good.

## Where the 26 disagreements come from

| Claude | Labeller 1 | n | reading |
|---|---|---|---|
| U | D | 12 | Records with no research output (profile text only). The notes say the label was inferred from department or degree ("No pubs but I'm guessing based off of his position", "MPH makes me believe dry"). The rubric says to judge the person, not the department, and to use U when there is too little. **Kept as U.** These do show that a reader expects clinicians with empty records to read as dry; that is a product question for the page, not an error in the key. |
| W | D | 6 | Bench labs on the record: rodent fear-circuit neuroscience, mouse liver autophagy, primate vaccine virology, stroke and glioma models, neuroendocrine assays, a two-paper record that is all bench. Claude and the model agree on W; five of the six have no note. **Kept as W**; these look like slips toward the default. |
| H | D | 4 | Hybrids (MRI physics plus rodent stroke models, haemophilia B-cell lab plus clinic, alveolar macrophage lab plus ICU education, placental methylation lab work within birth cohorts). Labeller 1 used H once in 150 rows, so the disagreement is about where the hybrid line sits rather than about these four. **Kept**; this is the case for a second, targeted hybrid sheet. |
| D | W | 3 | One is Katia Koelle, whose work is computational viral evolution (D is right); the other two are clinicians whose lab-sounding titles Claude set aside as namesakes or as a small share of a pathology practice. **Kept.** |
| D | U | 1 | Surgical pathology practice; kept. |

No row of `ml/gold_labels.csv` is changed on this check alone: in each group
the rubric supports Claude's label, and a single labeller cannot show which of
two readings is wrong. What the check does establish is that the accuracy the
page publishes is measured against one careful reader, and that a second
careful reader puts the model about 6 points lower on the people both could
judge. The page now says so (since v91, in the model note under "how this works").

## Also flagged in the notes

- H002 Kelly Bijanki: "SHE DOESN'T WORK AT EMORY ANYMORE". A stale record,
  not a label question; it belongs in the next scrape.

## Next

1. A second labeller on the same sheet. Two people give the human-human
   agreement, which says whether 86.8% vs 92.6% is the model or the reader.
2. A targeted hybrid sheet (the random 150 hold about 5 hybrids).
3. Decide whether profile-only clinical records should read as "leans dry"
   rather than "unclassified" on the page. If so, that is a rule change to the
   rubric and the key, made deliberately, not a correction of individual rows.
