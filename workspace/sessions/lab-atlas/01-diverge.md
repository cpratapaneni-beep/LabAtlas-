# Phase 1: Divergent Thinking -- Lab Atlas

> Session: `lab-atlas` | Generated: 2026-09-30 | Skill: `/sk-diverge`
> **Adaptation note:** StartupKit's Diverge phase is written for founders who have no idea yet. Lab Atlas already exists (v85, a working single-file atlas of 7,078 Emory investigators), so this phase diverges on **commercialization paths** instead of product ideas: who could pay, for what job, in what form. Blocks A-C were reconstructed from the v85 build and public sources rather than an interview; items tagged **[Founder to confirm]** need your input.

---

## Block A -- Craft Skills (what the team has already proven it can do)

Evidence is the v85 build itself (`Emory_Lab_Atlas_v85.html`, data generated 2026-09-29).

1. **Research-data engineering.** Merged nine source sheets on email then name into one record per person; 7,078 investigators across 9 schools/institutes and 107 units. [Data]
2. **Bibliometric linking.** PubMed matching on author affiliation/ORCID; 114,547 publication records attached to 5,178 investigators; 16,365 co-author pairs and 375 shared-grant pairs for the graph. [Data]
3. **Applied ML with honest evaluation.** Wet/dry model `wd-2026.09.3`: 934 labelled training records; held-out accuracy 91.6% (95% CI 88.7-94.3%) vs 14.6% for the previous rule-based version; calibrated confidence (Brier 0.037, AUC 0.889). [Data]
4. **LLM-assisted labelling under a rubric** (Claude labelled the training set; a human-check workflow exists in `ml/human_check`). [Data]
5. **Search UX.** Plain-language lab matching with related-term expansion and one-letter misspelling tolerance. [Data]
6. **Network visualisation.** Ego-graph of co-authors, shared grants and shared topics to 3rd degree. [Data]
7. **Scraping/collection tooling.** `scripts/gdbbs_scrape.py`, a browser collector, and `nih_reporter_verify.py` for NIH RePORTER verification. [Data]
8. **Design and editorial craft.** A polished, self-contained product with built-in provenance notes ("Two things this atlas cannot tell you"). [Data]
9. **Institutional navigation.** Won support from most of the Emory Pathways Center. [Founder claim]
10. **Student-side empathy.** The founders are (or recently were) the undergraduates this is for. [Assumption -- Founder to confirm]

## Block B -- Passions (why the team keeps building)

- Equal access to research experiences, regardless of who you know. [Assumption]
- Making opaque institutions legible (the product's own tagline is "Research, mapped"). [Data]
- Scientific honesty: the product states its own error rates and data gaps. [Data]

## Block C -- Skills to Learn (gaps between a great prototype and a licensable product)

1. Enterprise B2B sales to universities (procurement, budget cycles, RFPs).
2. Security & compliance paperwork: HECVAT 4 (321 questions), WCAG 2.1 AA + VPAT/ACR, FERPA-aware data handling, SSO (SAML/InCommon).
3. Multi-tenant web engineering (the product is currently one 37 MB offline HTML file).
4. Generalizing the data pipeline to any university (OpenAlex/ORCID/NIH RePORTER/NSF instead of Emory-specific sheets).
5. Contracts and IP: university licensing, Emory OTT negotiation, data-use terms.
6. Customer success: onboarding offices, training advisors, reporting outcomes.

---

## Block D -- Problems List (research-access ecosystem)

Tagged with Shapiro's 4 models: **5x** = 5x Easier, **Cheap** = Cheaper Version, **Copy** = copy from another market, **PLG** = product-led/network effect.

| # | Problem | Who feels it | Model |
|---|---------|--------------|-------|
| 1 | Students can't tell which of thousands of investigators run labs that fit their interests | Undergrads | 5x |
| 2 | Students can't tell wet-bench labs from computational/clinical groups | Undergrads | 5x |
| 3 | At Emory the model places only ~810 of 7,078 investigators (11%) on the wet-bench side, so blind emailing mostly misses | Undergrads, PIs | 5x |
| 4 | Cold-emailing is inequitable: an audit study emailing 6,548 professors as fictional prospective PhD students found faculty responded more often to white male names (undergrad-specific data not found) | First-gen and minoritized students | 5x |
| 5 | Posting platforms depend on faculty volunteering; at one university, voluntary use produced no participation gain while mandated use produced +57.5% | UR offices | 5x |
| 6 | Faculty inboxes fill with poorly targeted student emails | PIs | 5x |
| 7 | Nobody knows which labs actually take undergraduates, or how recently | Students, advisors | PLG |
| 8 | "Accepting students" flags go stale (v85's GDBBS roster shows 0 of 362 flagged accepting) | Grad students, programs | PLG |
| 9 | UR offices can't show equitable outcomes to provosts | UR directors | 5x |
| 10 | Advisors spend hours hand-curating lab lists per student | Pathways advisors | 5x |
| 11 | New faculty are invisible for their first 1-2 years | New PIs, students | 5x |
| 12 | Medical-school labs are invisible to college undergrads (different directories) | Undergrads, SOM PIs | 5x |
| 13 | First-year PhD students pick rotations from hundreds of faculty with weak information | Grad programs | 5x |
| 14 | Graduate programs track rotation availability in spreadsheets | Program admins | Cheap |
| 15 | Faculty can't find collaborators outside their department | PIs, research development offices | 5x |
| 16 | CTSA hubs must run "research networking" tools (Profiles RNS, VIVO) that are expensive to maintain | CTSA informatics teams | Cheap |
| 17 | Research-profile systems (Elsevier Pure, Symplectic) cost a lot and aren't built for students | Libraries, research offices | Cheap |
| 18 | Pre-health students need clinical research experience and can't find clinical research groups | Pre-health advisors | 5x |
| 19 | Summer research programs (SURE-type) manually match hundreds of applicants to mentors | Program directors | 5x |
| 20 | Visiting/high-school students have no map at all | Outreach programs | Copy |
| 21 | Prospective PhD applicants can't compare labs across universities | Applicants | PLG |
| 22 | NIH-funded labs expand after new awards, but students don't know who is hiring | Students | 5x |
| 23 | Offices lose institutional memory when advisors turn over | UR offices | 5x |
| 24 | Deans lack a picture of the research landscape (wet/dry mix, clusters, funding) | Provosts, deans | 5x |
| 25 | Industry partners can't find the right academic collaborator | Biotech BD, tech transfer | 5x |
| 26 | Tech-transfer offices can't map expertise quickly | OTT staff | 5x |
| 27 | Students can't write a credible first email to a PI | Undergrads | 5x |
| 28 | Students don't know research etiquette (hidden curriculum) | First-gen students | 5x |
| 29 | Labs lose good candidates to slow replies | PIs | 5x |
| 30 | Research-for-credit enrollment is tracked on paper forms | Registrars, UR offices | Cheap |
| 31 | International universities (UK, Canada, Australia) have the same problem | Non-US offices | Copy |
| 32 | Community colleges have no route into university labs | CC transfer students | Copy |
| 33 | Handshake treats research like a job posting and misses unposted labs | Career centers | 5x |
| 34 | Institutions need WCAG-compliant tools by the ADA Title II deadline (26 Apr 2027 for large public entities) | Public universities | 5x |
| 35 | Grant-funded training programs (NIH R25/T34-type, HHMI Inclusive Excellence) need mentor-matching infrastructure | Program PIs | 5x |

**Totals:** 10 skills, 3 passions, 6 skills to learn, 35 problems.

---

## Block D.5 -- Board Counsel (Opportunity & Vision)

- **Agreement.** The board would converge on the Zemurray lesson from the orchestrator: *"Those schmucks, what do they know, they're there, we're here."* You are closer to the undergraduate problem than any vendor. That proximity is the edge; it expires when you graduate.
- **Disagreement.** A Thiel-style "monopoly" lens says a campus directory is a small, contestable market and you should aim at the larger data asset (research-landscape intelligence). A Walton-style lens says win the small market obsessively first. Given ForagerOne's 200+ institutions, this session sides with a focused wedge (Phase 2) that still builds toward the data asset.
- **For you specifically.** Your rare skill is not the website. It is the pipeline that turns messy institutional records into an honest, classified map in weeks. Commercialize the pipeline.

---

## Block E -- Cross-Pollination (asset + problem = commercialization path)

Starred (★) items are recommended for scoring in Phase 2. [Founder to confirm stars]

| # | Asset + Problem | = Commercialization path |
|---|-----------------|--------------------------|
| ★1 | Atlas pipeline + problems 1-5, 12 | **Institution-wide undergraduate "lab discovery" license for research universities with academic medical centers** |
| ★2 | GDBBS roster tooling + problems 8, 13-14 | **Graduate rotation & recruitment atlas** for biomedical PhD umbrella programs |
| ★3 | Atlas + problems 5, 9 | **Discovery layer sold alongside ForagerOne/Handshake** (integration partner, not replacement) |
| ★4 | Graph + problems 15-17 | **Faculty collaboration / research-networking atlas** for research development offices and CTSA hubs |
| ★5 | Pipeline + problem 24 | **Research-landscape report** for provosts and deans (one-time or annual) |
| 6 | Recruiting record + problems 7, 22 | Student-facing "who is hiring" alerts (freemium consumer app) |
| 7 | Outreach coaching + problems 4, 27-28 | AI outreach coach licensed to access/equity programs (McNair, LSAMP, IMSD) |
| 8 | Pipeline + problem 21 | Cross-university lab search for PhD applicants (consumer or ad-supported) |
| 9 | Pipeline + problem 25 | Academic-partner scouting for biotech/pharma BD (a different, richer buyer) |
| 10 | Pipeline + problem 19 | Summer-program applicant-to-mentor matching module |
| 11 | Classifier + problem 18 | Clinical-research-experience finder for pre-health advising |
| 12 | Pipeline + problem 31 | International expansion (UK/Canada) once US playbook works |
| 13 | Data layer + problems 5, 33 | Data licensing to incumbents (ForagerOne, Handshake, Elsevier/Digital Science) |
| 14 | Pipeline + problem 35 | "Grant-fundable" infrastructure written into training-grant budgets |
| 15 | Pipeline + problem 26 | Expertise finder for tech-transfer offices |

**Total niche ideas: 15** (5 starred).

---

## Red Flags
- The product's Emory coverage is 87% School of Medicine (6,136 of 7,078) and only 112 Emory College STEM investigators, while the buyer we assume (the College's Pathways Center) serves college undergraduates. [Data] Coverage must match the buyer.

## Yellow Flags
- Several paths (6, 8) are consumer plays with no clear payer; they're listed for completeness, not recommended.

## Sources
- `Emory_Lab_Atlas_v85.html` embedded dataset (generated 2026-09-29).
- Milkman, Akinola & Chugh audit study as summarized by Behavioral Scientist: https://behavioralscientist.org/?p=7571
- Meyers (Notre Dame), ASEE 2026: https://nemo.asee.org/public/conferences/374/papers/51046/view
- DOJ ADA Title II extension summary (UPCEA, Apr 2026): https://upcea.edu/doj-extends-accessibility-deadline-to-april-2027-policy-matters-april-2026/
