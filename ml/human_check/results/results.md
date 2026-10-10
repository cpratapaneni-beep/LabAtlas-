# Human check of the wet/dry labels

People labelled a random sample of the locked test set blind, under the same rubric Claude used. The model calls below are the locked-test calls, from the version fitted on the training half only.

## Labeller 1: 150 of 150 labelled

Labels given: W 19, D 128, H 1, U 2; marked sure on 135.

**Agreement with Claude's labels**

| | agreement | 95% CI | Cohen's kappa |
|---|---|---|---|
| same label (W/D/H/U) | 82.7% | 76.0%-88.7% | 0.51 |
| wet vs not wet | 94.0% | 90.0%-97.3% | 0.75 |
| same label, both sure | 88.6% | | (n=88) |

| Labeller 1 \ Claude | W | D | H | U |
|---|---|---|---|---|
| W | 16 | 3 | 0 | 0 |
| D | 6 | 106 | 4 | 12 |
| H | 0 | 0 | 1 | 0 |
| U | 0 | 1 | 0 | 1 |

**The model, by these labels**

| judged by | model on the right side | 95% CI |
|---|---|---|
| Labeller 1 | 81.1% | 74.5%-87.2% |
| Claude (same people) | 92.7% | 87.9%-96.6% |

Difference (Labeller 1 minus Claude): -17.4 to -5.9 points. An interval that holds zero means the published accuracy stands on these labels.

After checking the lab's own web page or what they knew of it, Labeller 1 changed 8 labels. By those final labels the model is right for 80.4%.

## What to do next

`disagreements.csv` lists every person on whom anyone differs from Claude, with every label and note side by side. Go through it together; where the people are right, change that row of `ml/gold_labels.csv` (label, conf, and a note saying it was corrected by the human check) and rebuild with `scripts/build_atlas.sh`. The model retrains on the corrected labels and every figure on the page is recomputed.

