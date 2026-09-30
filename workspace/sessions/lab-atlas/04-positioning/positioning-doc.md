# Positioning Document: Lab Atlas
*Skill: sk-positioning | Generated: 2026-09-30 | Mode: standard | Research depth: Standard (score 6/9)*

## Executive Summary
Lab Atlas is a **lab discovery platform** for research universities. It maps every investigator on campus from publications, grants and directories, with no faculty data entry, and shows students what each lab studies, whether it works **at the bench or at a keyboard**, and who it works with. It's positioned **alongside** the posting tools offices already own (ForagerOne, Handshake), not against them. Best-fit buyers are undergraduate research offices at **universities with academic medical centers**, where thousands of investigators are invisible to undergraduates.

---

## The 5+1 Components

### 1. Competitive Alternatives -- Strength: **Strong** (well evidenced)
What offices and students would use if Lab Atlas didn't exist, in order of prevalence:
1. **Cold email + department pages + advisor lists** (status quo)
2. **ForagerOne** (posting marketplace; at Emory already)
3. **Handshake postings**
4. **Homegrown tools** (PairMe for GT/Emory BME)
5. **AI assistants** (students' first stop)
6. **Research-profile systems** (faculty-facing)
See `competitive-alternatives.md`.

### 2. Unique Attributes -- Strength: **Moderate** (two are unique; the rest are strong but copyable)
Grounded in v85 as built (dataset generated 2026-09-29):

| # | Attribute | Evidence | Unique? |
|---|-----------|----------|---------|
| U1 | **Measured wet-to-dry setting for every lab** | Model `wd-2026.09.3`: 91.6% held-out accuracy (95% CI 88.7-94.3%), calibrated confidence (Brier 0.037); 5,424 of 7,078 records classified [Data] | **Yes**, none found elsewhere |
| U2 | **Complete coverage with no faculty effort** | 7,078 investigators, 9 schools/institutes, 107 units, merged from source records [Data] | Partly (ForagerOne auto-creates profiles too) |
| U3 | **Evidence on every profile**: publications, NIH funding, grants | 114,547 publication records on 5,178 investigators; RePORTER verification layer [Data] | Partly (profile systems have publications, not for students) |
| U4 | **Plain-language search** with related terms and typo tolerance | "heart" finds cardiac and cardiovascular labs [Data] | No (AI assistants) |
| U5 | **Collaboration graph** (co-authors, shared grants, topics, 3 degrees) | 16,365 co-author pairs; 375 shared-grant pairs [Data] | No (Profiles RNS) |
| U6 | **Honest provenance**: every figure states its limits | "Two things this atlas cannot tell you" panel; confidence per call [Data] | **Yes** in practice (no competitor found that publishes error rates) |
| U7 | Placement record (nascent) | "My experience" submissions, aggregated monthly [Data]; no volume yet | Not yet an attribute; a roadmap asset |

**PAUSE -- Founder input required:** confirm, add or remove attributes. Things research can't see: data-refresh cadence, time to build a new university's atlas, faculty feedback so far, Pathways Center usage. **[Founder to confirm]**

### 3. Value Themes -- Strength: **Moderate-Strong**
| Theme | Attributes -> "so what?" -> value | Customer language |
|-------|-----------------------------------|-------------------|
| **V1. See every lab** | U2 + U4 + U5 -> students find labs no one told them about; the office stops chasing faculty to post | "who works on X here?" |
| **V2. Know the lab before you write** | U1 + U3 + U6 -> fewer, better-matched first emails; faculty get relevant inquiries; students stop emailing clinicians about bench work | "does this lab do wet work?", "write to the right lab" |
| **V3. Fair access you can measure** *(earned after the pilot)* | U7 + outreach coaching + outcomes reporting -> placements and equity numbers the provost cares about | "make the hidden door visible" |

V3 is **not** claimed until a pilot produces data (anti-aspirational rule).

### 4. Best-Fit Customers -- Strength: **Moderate** (inferred, not yet interviewed)
Characteristics that make a buyer care most:
1. A research university **with an academic medical center** (thousands of investigators; clinical departments dominate the directory).
2. A **pre-health / life-science-heavy** undergraduate body seeking bench or clinical research.
3. An office **measured on participation and equity**, with a data-minded champion.
4. A posting tool with **low faculty participation**, or no tool.
5. Director or associate-dean **budget authority for sub-threshold purchases**.

First targets fitting all five: Emory (design partner), then Southeast medical-center universities reachable through the Pathways Center's network. **[Founder to confirm list]**

### 5. Market Category -- Strength: **Strong**
**"Lab discovery platform"**: a subcategory (big fish, small pond) inside undergraduate-research tools. It sets the right expectations (complete, searchable, evidence-rich), avoids a head-to-head workflow comparison with ForagerOne, and leaves room for the V3 analytics later. See `market-category-analysis.md`.

### +1. Trend Overlay -- Strength: **Moderate**
**Austerity:** "make the tools you already pay for work better." Lab Atlas links every profile to the institution's ForagerOne or Handshake page, so it raises the return on existing spend instead of competing for it. "AI-powered" framing is deliberately **not** used.

---

## Validation Tests

### Neumeier Onliness Test
- **Basic:** "Lab Atlas is the only **lab discovery platform** that **maps every investigator on campus, and whether each lab works at the bench or the keyboard, without asking faculty to do anything**."
  - *Verdict:* **passes**. The combination of zero-effort coverage and a measured method classification wasn't found anywhere else (Wave 1 searches); U1 alone carries the "only".
- **Extended:** "Lab Atlas is the only lab discovery platform (WHAT) that maps every investigator, with a measured wet-to-dry setting, publications, funding and collaborators (HOW), for undergraduate research offices at medical-center universities (WHO) whose students must find fitting labs among thousands (WHERE) so they can write to fewer, better-matched labs (WHY) at a time when faculty won't maintain another profile and budgets are frozen (WHEN)."

### Ries/Trout Mental Ladder
| Check | Result |
|-------|--------|
| Simple enough to remember? | Yes: "every lab, bench to keyboard" |
| One clear rung? | Yes: **lab discovery** (not postings, not networking) |
| Rung available? | Yes: no vendor claims "lab discovery for students" |
| One sentence? | Yes (see the Moore statement) |

---

## Strategic Recommendations
1. **Never position as "a better ForagerOne."** Position as the discovery layer that makes the office's existing posting tool pay off. Build the deep links before the first sale.
2. **Lead every demo with the prospect's own campus** on the wet-to-dry axis (a preview built from open data).
3. **Earn V3:** design the Emory pilot to produce placement and equity numbers by May 2027.
4. **Close the coverage gap** for the Gold buyer: add Emory College's non-STEM and social-science faculty or clearly scope the product as STEM/biomedical.
5. **Rename for sale:** drop "Emory" from the product name (Emory policy restricts use of its name; see `05-offer.md`).

## Data Gaps & Limitations
- Best-fit profile is inferred; **zero buyer interviews** so far. Run the Phase 6 discovery calls.
- ForagerOne's actual discovery features weren't inspected (JS-rendered site). A demo could weaken or strengthen the U2/U3 claims.
- Faculty reaction to wet/dry labels and published emails is untested.

## Red Flags
- The Onliness claim leans on **one** unique attribute (U1). If ForagerOne adds method tags, the position narrows to coverage plus evidence, and both are copyable.

## Yellow Flags
- The "complement" posture could cap price. Buyers may see Lab Atlas as a nice-to-have add-on in a freeze.
- Hybrid labs are the model's weakest call (F1 0.43) [Data]. Don't let sales copy overstate precision.

## Sources
See `03-competitors/competitors-report.md` Sources, plus v85 dataset (generated 2026-09-29).
