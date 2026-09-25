# The wet/dry model

The atlas places every investigator on a wet/dry axis. Nothing in the source
data says whether a lab has a bench, so the setting has to be predicted. Until
v78 it came from a hand-weighted keyword score, "model v3.1". It claimed 87-92%
accuracy but had never been checked. This folder replaces it with a model
trained and tested on records that a person read and labelled.

## Result, on a locked test set

These are 400 investigators drawn at random and labelled by reading their
records, with no model output visible. None of them was used to fit or tune
anything. The table is from `report/evaluation.md`:

| | v3.1 | new model | difference (95% CI) |
|---|---|---|---|
| on the right side of the axis | 14.9% | **90.5%** | +70.9 to +80.3 pts |
| right, among records it placed | 25.8% | **93.6%** | +61.3 to +74.1 pts |
| given a setting at all | 57.7% | **96.7%** | +33.8 to +44.4 pts |
| wet labs found (F1) | 48.1% | **81.9%** | +24.6 to +43.9 pts |
| dry labs found (F1) | 8.2% | **95.7%** | +83.0 to +92.0 pts |
| hybrids found (F1) | 5.9% | 31.6% | -3.8 to +52.0 pts |

v3.1 almost never reached "dry". Of 306 test investigators labelled dry, it
called 64 of them wet, 86 hybrid and 143 unclassified. At Emory, where most
faculty are clinical, that made the axis close to meaningless.

Hybrids are still the weak spot. There are only 20 in the whole gold set, too
few to learn from or to measure well, and the page says so.

## Files

| file | what it is |
|---|---|
| `LABELLING_RUBRIC.md` | the definitions of W / D / H / U used for every label |
| `gold_labels.csv` | 800 hand labels: code, record index, name, email, train/test, label, confidence (1 sure, 2 judgment call), a one-line reason |
| `split.json` | the random draw (seed 20260925): `order` maps code G000-G799 to record index; `train` and `test` are the two halves |
| `relabel_check.csv` | 60 records re-labelled after all 800 were done, shuffled and under new codes, compared with the first pass: 59/60 agree (Cohen's kappa 0.95), 60/60 on wet vs not-wet |
| `wetdry.py` | the model: `cv`, `evaluate`, `predict` |
| `apply_wetdry.py` | writes predictions and the measured accuracy into an atlas HTML file |
| `report/` | the locked-test report, the metrics table with bootstrap intervals, and every test prediction next to its gold label |

## How it works

1. **Title model.** Logistic regression on word and word-pair TF-IDF of every
   paper title. It learns from the titles of gold wet people (1) and gold dry
   people (0). Each person's titles are weighted so a prolific author counts
   once, and the two sides get equal total weight.
2. **Context model.** The same, on the profile text, grant titles, departments,
   institutes and degrees. Profiles that turn out to be a patient's review
   are ignored.
3. **Stacker.** A small logistic model combines the per-person title scores
   (mean, upper quartile, share above 0.5, count), the context score, the
   grant count, degree flags, and the share of titles using bench,
   model-organism, computational and clinical word lists. It is trained on
   out-of-fold scores, so it never sees a score from a model that was fitted
   on the same person. It is not re-weighted, so its output is a calibrated
   P(wet). Hybrids count as half wet and half dry.
4. **Self-training.** Unlabelled records scored P ≥ 0.90 or ≤ 0.02 are added
   to the title model at 0.3 weight, and everything is refitted. Gold records,
   whether trained on or held out, are never in that pool. In
   cross-validation on the training half this raised accuracy from 90.9% to
   93.7%.
5. **Bands.** Wet from 0.70, leans wet from 0.45, hybrid between, leans dry to
   0.30, dry at 0.02 or below. They were chosen by cross-validation on the
   training half. A record with no titles is placed only if it has grants or
   a real profile *and* sits in the wet or dry band. Otherwise it is left
   unclassified.

The shipped model is refitted on all 800 labels, so it has seen the test half.
The test figures above are from the version trained on the training half
only.

## Honest limits

- **One labeller.** The same person labelled every record, so the test
  measures agreement with a careful reader, not with the labs. The blind
  re-label shows the labels are consistent. It cannot show whether they are
  right.
- **Namesakes.** A paper credited to the wrong person by a namesake misleads
  the model, exactly as it would mislead a reader.
- **Profile-only records.** Clinicians with no titles and no grants are left
  unclassified rather than called dry. That is deliberate.

## Re-running

```sh
python3 ml/wetdry.py cv       --data Emory_Lab_Atlas_v78.html --split ml/split.json --labels ml/gold_labels.csv
python3 ml/wetdry.py evaluate --data Emory_Lab_Atlas_v78.html --split ml/split.json --labels ml/gold_labels.csv --out ml/report
python3 ml/wetdry.py predict  --data Emory_Lab_Atlas_v78.html --split ml/split.json --labels ml/gold_labels.csv --out predictions.json
python3 ml/apply_wetdry.py Emory_Lab_Atlas_v78.html predictions.json ml/report/evaluation.csv -o atlas_out.html
```

Needs `numpy`, `scipy` and `scikit-learn`. Every run is deterministic;
re-running `predict` on v78 reproduces its stored predictions exactly. The gold
labels point at records by position. If the data is re-scraped or re-ordered,
`wetdry.py` notices that the names no longer match and stops rather than pin a
label on the wrong person.
