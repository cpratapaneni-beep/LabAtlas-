# Wet/dry model: locked test set

400 investigators, drawn at random and labelled by reading their records before any model output was looked at. None of them was used to fit or tune the model.

| metric | v3.1 (keyword score) | new model | difference (95% CI) |
|---|---|---|---|
| coverage | 57.2% (51.9%-62.4%) | 97.0% (95.2%-98.6%) | +34.7 to +45.3 pts |
| accuracy_all | 14.6% (11.2%-18.3%) | 90.8% (87.8%-93.8%) | +71.5 to +80.7 pts |
| accuracy_when_placed | 25.6% (19.9%-31.6%) | 93.6% (91.0%-95.9%) | +61.6 to +74.0 pts |
| macro_f1 | 20.9% (16.8%-25.4%) | 72.5% (64.1%-80.4%) | +43.2 to +60.2 pts |
| f1_W | 46.8% (36.6%-56.3%) | 87.1% (79.5%-93.3%) | +31.4 to +49.8 pts |
| f1_H | 7.7% (1.8%-15.7%) | 34.5% (10.5%-56.0%) | +5.8 to +47.8 pts |
| f1_D | 8.2% (4.2%-12.5%) | 95.8% (94.1%-97.3%) | +83.2 to +92.1 pts |
| wet_precision | 33.9% (25.0%-43.1%) | 84.6% (74.0%-93.5%) | +40.5 to +61.2 pts |
| wet_recall | 75.5% (63.4%-87.5%) | 89.8% (80.7%-97.6%) | +3.7 to +26.3 pts |
| unclear_left_unclassified | 90.3% (78.6%-100.0%) | 67.7% (50.0%-83.3%) | -40.7 to -5.3 pts |

Scored on the 369 test people whose gold label is wet, hybrid or dry; the 31 the labeller could not call are only used for the last row.

## v3.1

| gold \ predicted | wet side | hybrid | dry side | unclassified |
|---|---|---|---|---|
| wet | 37 | 1 | 0 | 11 |
| hybrid | 9 | 4 | 0 | 2 |
| dry | 63 | 84 | 13 | 145 |
| unclear | 1 | 2 | 0 | 28 |

## New model

| gold \ predicted | wet side | hybrid | dry side | unclassified |
|---|---|---|---|---|
| wet | 44 | 0 | 2 | 3 |
| hybrid | 5 | 5 | 4 | 1 |
| dry | 3 | 9 | 286 | 7 |
| unclear | 3 | 1 | 6 | 21 |

## Confidence

Every placed record carries a confidence: the chance that the call is on the right side. It was fitted to out-of-fold calls on the random training half only, then checked here. If it is honest, the share of right calls in each level matches the confidence it gave.

| level | test calls | mean confidence | right | 95% CI |
|---|---|---|---|---|
| high (90% and up) | 329 | 98.4% | 97.3% (320 of 329) | 94.9%-98.6% |
| moderate (70-89%) | 15 | 83.2% | 66.7% (10 of 15) | 41.7%-84.8% |
| low (under 70%) | 14 | 65.0% | 35.7% (5 of 14) | 16.3%-61.2% |
| all placed | 358 | 96.5% | 93.6% (335 of 358) | |

Brier score 0.045, against 0.060 for a flat confidence equal to the overall hit rate (lower is better). AUC 0.89: how often a right call gets a higher confidence than a wrong one.
