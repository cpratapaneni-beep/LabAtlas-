# Wet/dry model: locked test set

400 investigators, drawn at random and labelled by reading their records before any model output was looked at. None of them was used to fit or tune the model.

| metric | v3.1 (keyword score) | new model | difference (95% CI) |
|---|---|---|---|
| coverage | 57.7% (52.4%-62.9%) | 96.7% (94.9%-98.4%) | +33.8 to +44.4 pts |
| accuracy_all | 14.9% (11.4%-18.5%) | 91.6% (88.7%-94.4%) | +72.0 to +81.3 pts |
| accuracy_when_placed | 25.8% (20.1%-31.8%) | 94.7% (92.2%-96.9%) | +62.5 to +75.0 pts |
| macro_f1 | 20.7% (16.7%-24.9%) | 72.3% (60.7%-82.2%) | +40.0 to +62.0 pts |
| f1_W | 48.1% (38.4%-57.5%) | 85.5% (77.9%-92.0%) | +28.3 to +47.0 pts |
| f1_H | 5.9% (0.0%-12.9%) | 35.3% (0.0%-62.5%) | -3.8 to +57.1 pts |
| f1_D | 8.2% (4.2%-12.4%) | 96.2% (94.5%-97.6%) | +83.6 to +92.4 pts |
| wet_precision | 35.5% (26.8%-44.5%) | 81.0% (70.2%-90.6%) | +35.4 to +56.4 pts |
| wet_recall | 75.0% (62.7%-86.8%) | 90.4% (82.1%-97.8%) | +3.8 to +28.6 pts |
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
| wet | 47 | 0 | 2 | 3 |
| hybrid | 4 | 3 | 3 | 1 |
| dry | 7 | 3 | 288 | 8 |
| unclear | 4 | 1 | 5 | 21 |
