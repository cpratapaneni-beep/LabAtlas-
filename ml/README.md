# The wet/dry model

The atlas places every investigator on a wet/dry axis. Nothing in the source
data says whether a lab has a bench, so the setting has to be predicted. Until
v78 it came from a hand-weighted keyword score, "model v3.1". It claimed 87-92%
accuracy but had never been checked. This folder replaces it with a model
trained and tested on records that a person read and labelled.

## Result, on a locked test set

These are 400 investigators drawn at random and labelled by reading their
records, with no model output visible. None of them was used to fit or tune
anything. The table is from `report/evaluation.md` (model wd-2026.09.2, since v79):

| | v3.1 | new model | difference (95% CI) |
|---|---|---|---|
| on the right side of the axis | 14.9% | **91.6%** | +72.0 to +81.3 pts |
| right, among records it placed | 25.8% | **94.7%** | +62.5 to +75.0 pts |
| given a setting at all | 57.7% | **96.7%** | +33.8 to +44.4 pts |
| wet labs found (F1) | 48.1% | **85.5%** | +28.3 to +47.0 pts |
| dry labs found (F1) | 8.2% | **96.2%** | +83.6 to +92.4 pts |
| hybrids found (F1) | 5.9% | 35.3% | -3.8 to +57.1 pts |

Against the v78 model (90.5% on the right side), the only change whose
interval clears zero is wet recall: 82.7% to 90.4% (+1.6 to +15.1 pts).
Wet precision held at 81%.

This is the second time the test half has been scored. Nothing was tuned on
it either time: every choice below was made by cross-validation on the
training half and on the department-targeted labels, and the test half was
scored once, at the end.

v3.1 almost never reached "dry". Of 306 test investigators labelled dry, it
called 64 of them wet, 86 hybrid and 143 unclassified. At Emory, where most
faculty are clinical, that made the axis close to meaningless.

Hybrids are still the weak spot. There are 20 in the random gold set and 27
more among the department-targeted labels, still too few to learn from or to
measure well (11 in the test half), and the page says so.

## Files

| file | what it is |
|---|---|
| `LABELLING_RUBRIC.md` | the definitions of W / D / H / U used for every label |
| `gold_labels.csv` | 800 hand labels: code, record index, name, email, train/test, label, confidence (1 sure, 2 judgment call), a one-line reason |
| `gold_labels_dept.csv` | 220 more hand labels (codes A000-A219), chosen department by department (below). Training only; never in the test half |
| `department_types.csv` | every one of the 107 units, typed by hand by research character, with a one-line reason |
| `split.json` | the random draw (seed 20260925): `order` maps code G000-G799 to record index; `train` and `test` are the two halves |
| `relabel_check.csv` | 60 records re-labelled after all 800 were done, shuffled and under new codes, compared with the first pass: 59/60 agree (Cohen's kappa 0.95), 60/60 on wet vs not-wet |
| `wetdry.py` | the model: `cv`, `evaluate`, `predict` |
| `apply_wetdry.py` | writes predictions, the measured accuracy and the department block into an atlas HTML file |
| `report/confidence.json` | the confidence curve fitted on the training half, and how it held up on the test set |
| `department_report.py` | the department-by-department report: `report/departments.md`, `.csv`, and the `.json` the page reads |
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
5. **Bands.** Wet from 0.70, leans wet from 0.50, hybrid between, leans dry
   to 0.30, dry at 0.05 or below. They were chosen by cross-validation on the
   training half. A record with no titles is placed only if it has grants or
   a real profile *and* is a clear call (P ≥ 0.70 or ≤ 0.02). Otherwise it is
   left unclassified.

The shipped model is refitted on all 1,020 labels, so it has seen the test half.
The test figures above are from the version trained on the training half
only.

## Confidence

Every placed record carries a **confidence** next to its setting: the chance
that the call is right, meaning a careful reader of the record would put it on
the same side. It is not P(wet). A record at P(wet) 0.02 is confidently *dry*.

It is learnt, not asserted. The shipped model is refitted five times, each
time without a fifth of the 800 random gold labels, and the calls it makes on
the people it left out are compared with their hand labels. A small curve then
maps each call to how often calls like it were right.

- **Wet- and dry-side calls:** a logistic curve in the margin |logit P(wet)|,
  that is how far P(wet) sits from a coin toss. Only a margin was used.
  Adding the side, the number of titles, grants or a profile-only flag made
  held-out log-loss worse, because there are only a few dozen wrong calls to
  learn from (cross-validated on the training half).
- **Hybrid calls:** too few for a curve, and a hybrid sits in the middle by
  definition, so each one carries the share of hybrid calls that were right
  (Jeffreys-smoothed): about 39%.
- **Capped at 99%.** A few hundred checked records cannot support more.
- **Not fitted on the 220 department-targeted labels.** They were chosen
  because they are hard, so they would pull every figure down; including them
  (with a flag) was tried and made the fit worse.

Levels: high from 90%, moderate 70-89%, low below 70%.

Checked on the locked test set, with the curve fitted only to out-of-fold
calls on the training half (`report/confidence.json`,
`report/evaluation.md`):

| level | test calls | mean confidence | right | 95% CI |
|---|---|---|---|---|
| high | 321 | 98.4% | 98.1% (315 of 321) | 96.0-99.1% |
| moderate | 22 | 81.9% | 77.3% (17 of 22) | 56.6-89.9% |
| low | 14 | 52.3% | 42.9% (6 of 14) | 21.4-67.4% |

In every level the promised rate is inside the interval of what happened.
Brier score 0.037 against 0.050 for a flat figure; AUC 0.90, so a right call
nearly always gets a higher confidence than a wrong one. This was the third
time the test half was scored. The confidence was built and chosen on the
training half first, and nothing was changed after seeing the test.

Across the atlas: 4,961 calls rated high, 282 moderate and 189 low (every
hybrid is low). The page prints the figure under each mark in lists, in full
on each profile (with how test calls at that level did), in tooltips and on
the P(wet) ridge, and the glyph's stain now follows it.

## Department by department

Every one of the 107 units was read and typed by its research character
(`department_types.csv`): basic science 32, clinical 31, translational
centre 12, population health 10, administrative 9, behavioural/social 4,
quantitative 4, engineering 2, genetics, pathology & lab medicine and
nursing 1 each. That typing does three jobs.

**It chose who to label next.** Where the model's side was a surprise for
the unit's character (a "dry" call in a basic-science department, a "wet"
call in a clinical one, anyone in a translational centre), 220 more
investigators were read and labelled blind, spread across unit types:
82 wet, 82 dry, 27 hybrid, 29 unclear (`gold_labels_dept.csv`). They are
the hardest records in the atlas, so they are only ever used for training
or as a held-out hard-case set, never mixed into the random test half.

**It was tested as a model feature, and rejected.** Three ways to feed the
department in were tried: the unit type, the mean P(wet) of a person's
colleagues, and that mean crossed with their own title score. On the
random training half (cross-validated) none moved accuracy (94.8% base,
94.5-94.9% with any of them). On the 220 hard cases, held out, they hurt:

| variant | hard cases on the right side | hybrid F1 |
|---|---|---|
| base (800 random labels) | 66.0% | 0.33 |
| + department features | 62.3% | 0.12 |
| + the 220 targeted labels | **69.6%** | **0.38** |
| + targeted labels + department features | 66.5% | 0.18 |
| + targeted labels + colleagues' mean only | 66.0% | 0.22 |

The hard cases are exactly the people who don't match their department:
the physician-scientist with a bench lab in Medicine, the pathologist in
a basic-science programme, the epidemiologist in a translational centre.
A department prior pulls them toward the wrong side. So each person is
placed from their own work only (`USE_DEPT = False` in `wetdry.py`; the
code is kept so the test can be re-run). The targeted labels are kept:
they raised wet F1 in cross-validation (0.887 to 0.903) and hybrid F1
(0.17 to 0.32).

**It reports accuracy by department.** `report/departments.md` has every
unit's wet/hybrid/dry mix, how many of its people were hand-labelled, and
test agreement. By character, on the locked test set: clinical 92%
(258/279), population health 89%, basic science 83% (19/23), and
translational centres the weakest at 68% (27/40). The page shows each
unit's character and its hand-checked figures on the unit card and in
every profile.

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
L="--split ml/split.json --labels ml/gold_labels.csv --extra ml/gold_labels_dept.csv"
python3 ml/wetdry.py cv       --data Emory_Lab_Atlas_v80.html $L
python3 ml/wetdry.py evaluate --data Emory_Lab_Atlas_v80.html $L --out ml/report
python3 ml/wetdry.py predict  --data Emory_Lab_Atlas_v80.html $L --out predictions.json
python3 ml/department_report.py Emory_Lab_Atlas_v80.html predictions.json ml/report/test_predictions.csv $L --out ml/report
python3 ml/apply_wetdry.py Emory_Lab_Atlas_v80.html predictions.json ml/report/evaluation.csv \
    --departments ml/report/departments.json --confidence ml/report/confidence.json -o atlas_out.html
```

`--extra` adds the department-targeted labels to training. `wetdry.py`
refuses an extra label that points at a test-half or already-labelled
person.

Needs `numpy`, `scipy` and `scikit-learn`. Every run is deterministic;
re-running `predict` on v80 reproduces its stored predictions exactly. The gold
labels point at records by position. If the data is re-scraped or re-ordered,
`wetdry.py` notices that the names no longer match and stops rather than pin a
label on the wrong person.
