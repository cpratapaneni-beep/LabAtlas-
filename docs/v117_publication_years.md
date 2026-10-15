# Publication years and the disclaimer (v117)

## What was checked

Every publication on file (111,586 records across 7,078 investigators) was compared with an outside source.

- **Papers with a PubMed ID** (59,560 records, 45,197 distinct papers): the stored year was compared with PubMed's own record, fetched for every paper.
  - 58,390 had PubMed's year exactly.
  - 588 had the paper's online-first year rather than its issue year.
  - 66 were one year off.
  - 503 were wrong or unreadable: 455 stored a full date such as "2026 Jan 15" or an ORCID timestamp instead of a year, and 48 had no year.
- **Papers without a PubMed ID** (ORCID, Crossref, OpenAlex): random samples were checked against Crossref.
  - Of those Crossref could match: 24 of 29 ORCID records exact and 3 within a year; 20 of 21 Crossref records exact.

No publication was lost between versions. The counts per person have been the same since v93.

## What changed in v117

- Every paper with a PubMed ID now carries PubMed's year (1,157 records changed).
- The other papers carry the year read out of their stored date, where they had a full date or timestamp.
- 416 records still have no year. They sort last.
- Supplementary figures, tables and data files that people attached to their ORCID record stay in the full list, but are never shown among the five most recent.

## The disclaimer

Up to v93, the "Before you read the numbers" note (wet/dry predictions and NIH funding) opened by itself the first time someone entered the atlas.

v94's website audit replaced that with the one-line note at the top of the atlas. Its "How we know" link and the ⓘ buttons still opened the full note.

v117 restores the v93 behaviour. The note opens once per visit, on entering the atlas, and the one-line note and buttons are unchanged.
