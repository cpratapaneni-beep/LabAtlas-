# The wet/dry model

The atlas places every investigator on a wet/dry axis. Nothing in the source
data says whether a lab has a bench, so the setting has to be predicted. Until
v78 it came from a hand-weighted keyword score, "model v3.1". It claimed 87-92%
accuracy but had never been checked. This folder replaces it with a model
trained and tested on records that a person read and labelled.

## Result, on a locked test set

These are 400 investigators drawn at random and labelled by Claude reading their
records, with no model output visible. None of them was used to fit or tune
anything. The table is from `report/evaluation.md` (model wd-2026.09.3, v82),
scored against the labels as revised by the hybrid audit (below):

| | v3.1 | new model | difference (95% CI) |
|---|---|---|---|
| on the right side of the axis | 14.6% | **91.6%** | +72.4 to +81.4 pts |
| right, among records it placed | 25.4% | **94.7%** | +63.1 to +75.3 pts |
| given a setting at all | 57.7% | **96.7%** | +33.8 to +44.4 pts |
| wet labs found (F1) | 46.5% | **89.1%** | +33.5 to +52.4 pts |
| dry labs found (F1) | 8.2% | **96.1%** | +83.5 to +92.4 pts |
| hybrids found (F1) | 7.6% | 42.9% | +13.0 to +55.2 pts |

This is the fourth time the test half has been scored, and the first time
any of its labels changed: the hybrid audit revised 4 of its 400 labels (3 wet
and 1 dry became hybrid). So the v81 model and this one are shown against
both versions of the labels:

| labels | model | right side | hybrid F1 | wet precision | wet recall |
|---|---|---|---|---|---|
| before the audit | v81 (P(wet) bands) | 91.6% | 35.3% | 81.0% | 90.4% |
| before the audit | v82 (mix of work) | 91.3% | 33.3% | 88.5% | 88.5% |
| after the audit | v81 (P(wet) bands) | 91.3% | 38.1% | 77.6% | 91.8% |
| after the audit | v82 (mix of work) | 91.6% | 42.9% | 86.5% | 91.8% |

The differences are small and their intervals are wide (15 test hybrids). The
honest summary is: no loss of accuracy, fewer bench-and-computation labs
called plain wet, and settings that now say what mix of work a record shows.

v3.1 almost never reached "dry". Of 306 test investigators labelled dry, it
called 64 of them wet, 86 hybrid and 143 unclassified. At Emory, where most
faculty are clinical, that made the axis close to meaningless.

Hybrids are still the weak spot. There are 26 in the random gold set and 29
more among the department-targeted labels, still too few to learn from or to
measure well (15 in the test half), and the page says so.

## Files

| file | what it is |
|---|---|
| `LABELLING_RUBRIC.md` | the definitions of W / D / H / U used for every label |
| `gold_labels.csv` | 800 labels Claude assigned by reading each record: code, record index, name, email, train/test, label, confidence (1 sure, 2 judgment call), a one-line reason |
| `gold_labels_dept.csv` | 220 more labels, assigned the same way (codes A000-A219), chosen department by department (below). Training only; never in the test half |
| `department_types.csv` | every one of the 107 units, typed by Claude by research character, with a one-line reason |
| `hybrid_audit.csv` | the 57 gold records re-read for missed hybrids, with each decision and its reason |
| `lab_corrections.csv` | settings reported by people who know the lab; shown on the page in place of the model's |
| `human_check/` | the blind check of those labels by people: a labelling workbook of 150 random test records, its key, and how to run it (`make_human_check.py` builds it, `human_check.py` scores it) |
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
5. **Setting.** P(wet) decides the side: the wet side from 0.50, the dry
   side at 0.30 or below, hybrid between. The mix of the record's titles then
   decides where on its side it sits (see "Hybrids and the mix of work"). How
   sure the call is lives in the confidence, not in the setting. A record with
   no titles is placed only if it has grants or a real profile *and* is a clear
   call (P ≥ 0.70 or ≤ 0.02); otherwise it is left unclassified.

The shipped model is refitted on all 1,020 labels, so it has seen the test half.
The test figures above are from the version trained on the training half
only.

## Confidence

Every placed record carries a **confidence** next to its setting: the chance
that the call is right, meaning a careful reader of the record would put it on
the same side. It is not P(wet). A record at P(wet) 0.02 is confidently *dry*.

It is learnt, not asserted. The shipped model is refitted five times, each
time without a fifth of the 800 random gold labels, and the calls it makes on
the people it left out are compared with their gold labels. A small curve then
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

## Hybrids and the mix of work

Until v81 a setting was a band of P(wet): "leans wet" meant P between 0.50 and
0.70, that is, the model was unsure. Two labs showed why that was wrong.
- **Rafick-Pierre Sékaly** runs wet-bench immunology *and* systems immunology,
  multi-omics and machine learning, yet sat at P(wet) 0.98, "wet". The
  immunology words in every title (T cells, SIV, HIV) outweighed the method.
- **Charles Bou Nader** is mostly wet but has fully dry projects. That should
  read as "leans wet".

Since the confidence (above) now says how sure a call is, the setting is free
to say what mix of work the record shows:

| setting | means |
|---|---|
| wet | bench work throughout |
| leans wet | mostly bench, with a real share (10% or more of titles) of computational, omics, modelling, cohort or trial work |
| hybrid | bench work alongside 30% or more such titles, or P(wet) between 0.30 and 0.50 |
| leans dry | mostly non-bench, with 10% or more bench titles that use no dry method |
| dry | no bench work |

Each title is read twice:
- by the title model, for whether it reads as bench work;
- by `DRY_METHOD` in `wetdry.py`, for whether its *method* is computation,
  prediction, omics analysis, a cohort or a trial, whatever its topic.

"Multi-omics analyses reveal that HIV-1 alters CD4 T cell immunometabolism" is
both, which is what a systems lab looks like.

The 30% line was chosen on the random training half (out-of-fold). There it
raised hybrid F1 from 0.32 to 0.48 and accuracy from 95.7% to 96.2%. The 10%
lines are definitions, since no gold label says "leans". A dry-side hybrid
rule lost accuracy, because computational genomics titles read as bench work
to the title model, so there is none.

**The audit of Claude's labels.** The same problem was in the answer key.
Every gold record whose titles mixed bench work with a real share of
dry-method titles (or the reverse) was flagged by a rule on the titles alone,
57 records, and re-read under the rubric. Eight were hybrids that Claude had
labelled wet or dry. Peter Kasson, Melissa Kemp, Yesim Gokmen-Polar, Timothy
Gershon, Juliete Silva, Nicholas Boulis and Steven Bosinger were bench labs
paired with computation or clinical studies, labelled wet; David Jaye was
labelled dry. Four of the eight are in the test half. Every decision and its
reason is in `hybrid_audit.csv`, and each revised row of the gold files keeps
its old label in the note. Claude's reading leaned toward calling
bench-plus-computation labs wet; the human check (`human_check/`) is the way
to find what else it leans on.

**Corrections from people who know the lab.** Some mixes do not show in the
public record: Bou Nader's four titles and profile are all bench work.
`lab_corrections.csv` holds settings reported by people who know the lab, with
the reason, source and date. `apply_wetdry.py --corrections` puts them on the
page in place of the model's setting, marked "corrected by someone who knows
the lab", with the model's own call kept beside it. They do not train the
model or change the test.

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
unit's wet/hybrid/dry mix, how many of its people were labelled, and
test agreement. By character, on the locked test set: clinical 92%
(258/279), population health 89%, basic science 83% (19/23), and
translational centres the weakest at 68% (27/40). The page shows each
unit's character and its hand-checked figures on the unit card and in
every profile.

## Honest limits

- **The labels are Claude's, not a person's.** Claude assigned every gold
  label by reading the record under `LABELLING_RUBRIC.md`, so every figure
  here measures agreement with that reading, not with the labs. The blind
  re-label shows the labels are consistent. It cannot show whether they are
  right: if the reading is off in some systematic way, the model learns the
  same bias and the test cannot see it. `human_check/` is the fix. People who
  know Emory's labs label 150 random test records blind, and
  `human_check.py` reports how often they agree with Claude and whether the
  published accuracy holds up by their labels. Until that is run, treat the
  figures as agreement with a careful machine reader.
- **Namesakes.** A paper credited to the wrong person by a namesake misleads
  the model, exactly as it would mislead a reader.
- **Profile-only records.** Clinicians with no titles and no grants are left
  unclassified rather than called dry. That is deliberate.

## Re-running

```sh
L="--split ml/split.json --labels ml/gold_labels.csv --extra ml/gold_labels_dept.csv"
python3 ml/wetdry.py cv       --data Emory_Lab_Atlas_v83.html $L
python3 ml/wetdry.py evaluate --data Emory_Lab_Atlas_v83.html $L --out ml/report
python3 ml/wetdry.py predict  --data Emory_Lab_Atlas_v83.html $L --out predictions.json
python3 ml/department_report.py Emory_Lab_Atlas_v83.html predictions.json ml/report/test_predictions.csv $L --out ml/report
python3 ml/apply_wetdry.py Emory_Lab_Atlas_v83.html predictions.json ml/report/evaluation.csv \
    --departments ml/report/departments.json --confidence ml/report/confidence.json \
    --corrections ml/lab_corrections.csv -o atlas_out.html
```

`--extra` adds the department-targeted labels to training. `wetdry.py`
refuses an extra label that points at a test-half or already-labelled
person.

Needs `numpy`, `scipy` and `scikit-learn`. Every run is deterministic;
re-running `predict` on v83 (whose records are v82's, byte for byte) reproduces its stored predictions exactly. The gold
labels point at records by position. If the data is re-scraped or re-ordered,
`wetdry.py` notices that the names no longer match and stops rather than pin a
label on the wrong person.
