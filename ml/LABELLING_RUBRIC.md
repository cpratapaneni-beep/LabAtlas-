# Wet / dry / hybrid: the labelling rubric

The gold labels in `gold_labels.csv` were assigned by reading each person's own
record — their publication titles, profile description, grant titles,
department and degrees — **without seeing either model's output**. The label
describes where the person's *own research output* sits on the atlas's axis:
whether the work is done at a lab bench or not.

## Labels

**W — wet.** Most of the output rests on bench or laboratory experiments that
the group itself runs: cells, molecules, proteins, nucleic acids, microbes,
tissues and specimens processed in a lab; animal models (mouse, rat,
non-human primate, zebrafish, fly, worm); chemistry and synthesis; structural
biology (crystallography, cryo-EM, NMR of molecules); biomaterials and devices
built and tested at the bench; electrophysiology in tissue or animals;
experimental imaging of specimens or animals.

**D — dry.** Most of the output is research without a bench: computational
biology, bioinformatics, statistics and methods; epidemiology and population
health; clinical research on patients, records, registries or trials; case
reports and case series; surveys, interviews, qualitative and behavioural
research; health services, policy, economics and education; image
interpretation and radiology outcomes. *Clinical research counts as dry here*
because the atlas's axis is bench versus no bench, not laboratory versus
computer.

**H — hybrid.** Both modes are a substantial, deliberate part of the output —
roughly a quarter or more each — or the group explicitly pairs bench
experiments with computational or clinical-cohort analysis as its method
(for example, mouse models alongside patient cohorts; sequencing experiments
alongside the bioinformatics built to read them).

**U — cannot tell.** Too little to judge: no description and only a couple of
uninformative titles, or only editorials, commentaries and guidelines.

## Confidence

Each label carries a confidence: **1** sure, **2** likely. Evaluation is
reported on all labels and, separately, on the sure ones.

## Reading rules

- Judge the person, not the department. A pathologist can run a bench lab or
  only read slides; a neuroscientist can be entirely computational.
- Weigh the bulk of the titles, not the most striking one. A clinician with one
  mouse paper in forty clinical papers is dry.
- Co-authorship on large consortia or trials counts toward what it is: a
  clinician's many multi-centre trial papers are dry.
- Publications credited to a namesake (a clearly different field, a different
  era) are set aside when they are obvious.
- Profile boilerplate (clinic addresses, board certifications, languages
  spoken) says a person is a clinician; it does not by itself say whether they
  also run a bench.

## Why a person labelled these, and what to do about it

The labels were assigned by Claude, reading each record in full, because no
human-checked labels existed and accuracy cannot be measured without them.
Every label is in `gold_labels.csv` with the person's name, so any of them can
be checked or overruled. `evaluate.py` re-scores both models against whatever
labels the file holds, so correcting a label and re-running it is all a
re-check takes.
