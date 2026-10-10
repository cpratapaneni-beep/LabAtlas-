# v103 review: wet/dry misses, copy and search

## Why David Yu was classified dry

David Yu (record 6031) runs a bench lab in Radiation Oncology and Winship Cell & Molecular Biology. The model gave him P(wet) = 0.286, just under the 0.30 dry line. The mix rule then made that "leans dry" with 73% confidence. Four things combined:

1. **Department features are off.** `USE_DEPT = False` in `ml/wetdry.py`, so a Winship basic-science unit adds nothing.
2. **Few titles, and the wrong ones.** Only six recent titles were on record. Two were imaging-AI collaborations, and one paper (ROBIN) was listed twice. `titles_of` misses duplicates when a suffix is appended to the title.
3. **Grants count as loose words.** His SAMHD1 DNA-repair R01s and a Cancer Biology T32 only enter the context text. They carry no weight of their own.
4. **The source data had it right.** Its keyword label was wet (score 75). The gold label in `ml/gold_labels.csv` is hybrid.

**Fix in v103:** a maintainer correction to Wet, recorded in `ml/lab_corrections.csv`. The profile shows "corrected by someone who knows the lab" and what the model alone said.

## Similar cases

The scan looked for records marked dry or leans dry that still show bench signals (wet grants, basic-science units, bench words in the bio). It found 21.

**Gold label is hybrid, model says dry (7, wrong):**

| Record | Name |
|---|---|
| 6031 | David Yu (corrected in v103) |
| 6361 | Phillip Zhe Sun |
| 267 | Waitman Aumann |
| 3546 | Morgan L. McLemore |
| 574 | Nicholas Boulis |
| 429 | Jacob E. Berchuck |
| 142 | Susan Allen |

**No gold label, worth a look (8):** Sunil Badve (294), Vivien Sheehan (4990), Nadine Rouphael (4652), C. Moreno (3736), Andrea Moffitt (3688), Christian Larsen (3057), Aparna Kesarwala (2759), Jennifer Felger (1524).

**Correctly dry:** pathologists Neill, Mejbel and Linsheng Zhang (gold dry), and Katia Koelle (gold dry, computational).

**Model fixes:** better title de-duplication, turning the department signal back on, and giving grant titles their own feature. Each of these needs the model retrained and re-evaluated.

## Copy review (SlopMonster)

Each screen's visible text was run through `tools/deslop.py` from SlopMonster.

| Screen | Score /5 |
|---|---|
| Landing | 4 |
| Atlas | 4 |
| Find a lab | 3–4 |
| Directory | 3 |
| Profile | 1 |
| Mentors | 4 |
| Notes | 3 |

**Rewritten in v103:**
- The repeated "predicted, not recorded" contrast (banner, rail, profile, unclassified note).
- Semicolon chains in the atlas lede, profile side note, keyword-label sentence, profile footer, privacy note, photo strip, sphere caption and footer.
- The jargon-heavy "My experience" intro.

**Ignored as false positives:**
- Student counts are real data.
- "Innovate" is quoted from a faculty bio.
- One rule-of-three is a paper title.

**Still flagged:** the Notes page. It is semicolon-heavy, uses technical terms (TF-IDF, P(wet)) and has one rule-of-three.

## Directory vs Find a lab

The two pages now do different jobs:

- **Find a lab:** describe the work you want to do and get labs ranked by topic.
  - Topic chips are now general areas.
  - The autofill on the unit box is replaced by a plain list of schools and departments.
  - The name field moved to the Directory.
  - Rarely used filters fold under "More filters".
- **Directory:** look a person up by name, or browse a school and its departments.
  - One bar holds search, school, department and a Filters button.
  - Active filters show as removable chips.
  - Name sorting adds letter headings.
  - Rows show up to three general research areas instead of raw keywords.
  - When a query reads like a topic rather than a name, the page offers to run it in Find a lab.
