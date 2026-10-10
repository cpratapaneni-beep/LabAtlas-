# Wet/dry model: locked test set

400 investigators, drawn at random and labelled by reading their records before any model output was looked at. None of them was used to fit or tune the model.

| metric | v3.1 (keyword score) | new model | difference (95% CI) |
|---|---|---|---|
| coverage | 57.7% (52.4%-62.9%) | 96.7% (94.9%-98.4%) | +33.8 to +44.4 pts |
| accuracy_all | 14.6% (11.2%-18.3%) | 91.6% (88.6%-94.3%) | +72.4 to +81.4 pts |
| accuracy_when_placed | 25.4% (19.7%-31.3%) | 94.7% (92.2%-96.9%) | +63.1 to +75.3 pts |
| macro_f1 | 20.8% (16.7%-25.3%) | 76.0% (67.0%-84.0%) | +46.8 to +63.1 pts |
| f1_W | 46.5% (36.4%-56.0%) | 89.1% (82.1%-95.1%) | +33.5 to +52.4 pts |
| f1_H | 7.6% (1.8%-15.7%) | 42.9% (18.2%-64.3%) | +13.0 to +55.2 pts |
| f1_D | 8.2% (4.2%-12.5%) | 96.1% (94.4%-97.6%) | +83.5 to +92.4 pts |
| wet_precision | 33.6% (24.8%-42.7%) | 86.5% (76.0%-94.9%) | +42.9 to +63.2 pts |
| wet_recall | 75.5% (63.4%-87.5%) | 91.8% (83.9%-98.2%) | +5.4 to +28.9 pts |
| unclear_left_unclassified | 83.9% (70.0%-96.3%) | 67.7% (50.0%-83.3%) | -32.3 to +0.0 pts |

Scored on the 369 test people whose gold label is wet, hybrid or dry; the 31 the labeller could not call are only used for the last row.

## v3.1

| gold \ predicted | wet side | hybrid | dry side | unclassified |
|---|---|---|---|---|
| wet | 37 | 1 | 0 | 11 |
| hybrid | 9 | 4 | 0 | 2 |
| dry | 64 | 85 | 13 | 143 |
| unclear | 1 | 4 | 0 | 26 |

## New model

| gold \ predicted | wet side | hybrid | dry side | unclassified |
|---|---|---|---|---|
| wet | 45 | 0 | 1 | 3 |
| hybrid | 4 | 6 | 4 | 1 |
| dry | 3 | 7 | 287 | 8 |
| unclear | 3 | 2 | 5 | 21 |

## Confidence

Every placed record carries a confidence: the chance that the call is on the right side. It was fitted to out-of-fold calls on the random training half only, then checked here. If it is honest, the share of right calls in each level matches the confidence it gave.

| level | test calls | mean confidence | right | 95% CI |
|---|---|---|---|---|
| high (90% and up) | 322 | 98.4% | 97.8% (315 of 322) | 95.6%-98.9% |
| moderate (70-89%) | 19 | 83.4% | 89.5% (17 of 19) | 68.6%-97.1% |
| low (under 70%) | 16 | 56.8% | 37.5% (6 of 16) | 18.5%-61.4% |
| all placed | 357 | 95.8% | 94.7% (338 of 357) | |

Brier score 0.037, against 0.050 for a flat confidence equal to the overall hit rate (lower is better). AUC 0.89: how often a right call gets a higher confidence than a wrong one.
