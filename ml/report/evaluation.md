# Wet/dry model: locked test set

400 investigators, drawn at random and labelled by reading their records before any model output was looked at. None of them was used to fit or tune the model.

| metric | v3.1 (keyword score) | new model | difference (95% CI) |
|---|---|---|---|
| coverage | 57.7% (52.4%-62.9%) | 96.7% (94.9%-98.4%) | +33.8 to +44.4 pts |
| accuracy_all | 14.9% (11.4%-18.5%) | 90.5% (87.5%-93.4%) | +70.9 to +80.3 pts |
| accuracy_when_placed | 25.8% (20.1%-31.8%) | 93.6% (91.0%-96.0%) | +61.3 to +74.1 pts |
| macro_f1 | 20.7% (16.7%-24.9%) | 69.7% (59.2%-79.5%) | +38.6 to +58.8 pts |
| f1_W | 48.1% (38.4%-57.5%) | 81.9% (73.6%-89.4%) | +24.6 to +43.9 pts |
| f1_H | 5.9% (0.0%-12.9%) | 31.6% (0.0%-57.1%) | -3.8 to +52.0 pts |
| f1_D | 8.2% (4.2%-12.4%) | 95.7% (94.0%-97.2%) | +83.0 to +92.0 pts |
| wet_precision | 35.5% (26.8%-44.5%) | 81.1% (69.8%-91.1%) | +35.6 to +56.6 pts |
| wet_recall | 75.0% (62.7%-86.8%) | 82.7% (72.7%-92.9%) | -4.9 to +20.9 pts |
| unclear_left_unclassified | 83.9% (70.0%-96.3%) | 67.7% (50.0%-83.3%) | -32.3 to +0.0 pts |

Scored on the 369 test people whose gold label is wet, hybrid or dry; the 31 the labeller could not call are only used for the last row.

## v3.1

| gold \ predicted | wet side | hybrid | dry side | unclassified |
|---|---|---|---|---|
| wet | 39 | 1 | 0 | 12 |
| hybrid | 7 | 3 | 0 | 1 |
| dry | 64 | 86 | 13 | 143 |
| unclear | 1 | 4 | 0 | 26 |

## New model

| gold \ predicted | wet side | hybrid | dry side | unclassified |
|---|---|---|---|---|
| wet | 43 | 3 | 3 | 3 |
| hybrid | 2 | 3 | 5 | 1 |
| dry | 8 | 2 | 288 | 8 |
| unclear | 4 | 1 | 5 | 21 |
