# Phase 9: AI Skills Match -- Lab Atlas

> Session: `lab-atlas` | Generated: 2026-09-30 | Skill: `/sk-skills`
> Inputs: Gold niche (`02-niches.md`), offer (`05-offer.md`), money model (`07-money-model.md`).
> **Recap:** you serve UR offices at medical-center universities with the *Every Lab in 45 Days* program ($15K list Standard). Which AI skills amplify it?
> **Adaptation:** the StartupKit catalog prices skills as agency services (setup + monthly). For Lab Atlas, each skill is judged in two roles: as a **product module** sold to universities, and as an **internal operating tool** for a tiny team.

---

## Step 1: Skills Catalog Reference
| Skill | What it does | Catalog pricing | Relevant when |
|-------|-------------|-----------------|---------------|
| Brand Clone | Writes in a specific person's voice | $1-2K setup + $200/mo | Voice consistency matters |
| Weekly Autopilot Report | Auto-pulls metrics into a formatted report | $1.5-3K setup + $300-500/mo | Recurring reporting burden |
| Content Atomizer | 1 long piece -> 15+ channel pieces | $2-3.5K setup + $500/mo | Content-heavy GTM |
| Proposal Machine | Proposal/SOW from a 10-minute intake | $1.5-2.5K setup + $300/mo | 4+ proposals per month |
| Client Radar | Flags renewals, churn risk, upsell signals | $2-3.5K setup + $400/mo | 20+ ongoing accounts |
| Support Shield | First-response agent on a knowledge base | $3-5K setup + $500/mo | 50+ support tickets per day |
| Outreach Engine | Researches a target; drafts personalized outreach | $2.5-4K setup + $400/mo | Outbound prospecting |

---

## Step 2: Evaluation Against the Gold Niche

### Outreach Engine -> **"Outreach Coach"** (product) -- Fit: **STRONG**
- **Why:** it is literally the "facilitating communication between undergraduates and PIs" half of your mission, which v85 doesn't do yet (it shows an email address and "Confirm before you write").
- **Product design:** for a chosen lab, draft a first email grounded in the record (a recent paper, the lab's methods, the student's stated interest), coach etiquette (length, ask, availability), and enforce **guardrails**: a weekly send limit per student, blocking labs flagged "not taking students", and no mass-mailing.
- **Equity angle:** directly targets the documented response gap (audit of 6,548 professors). It's a hidden-curriculum equalizer.
- **Risk:** done badly, it makes spam cheaper. Guardrails are the product, and the pitch to faculty ("fewer, better emails").
- **Internal use too:** research each UR director's campus before a call (see `08-lead-strategy.md`).

### Weekly Autopilot Report -> **"Semester Impact Report"** -- Fit: **STRONG**
- **Why:** UR directors must show participation and equity numbers; ForagerOne sells "actionable analytics". Lab Atlas has none today.
- **Design:** auto-generated each semester (monthly in higher tiers): students using, labs contacted, reply and placement rates, privacy-safe equity breakdowns, coverage and freshness of the atlas.

### Client Radar -> **"Lab Radar"** (product) + account radar (internal) -- Fit: **STRONG**
- **Product twist:** students follow labs; Lab Radar alerts them when a followed lab gets a **new NIH award** or publishes. New funding often means hiring. Built from the monthly refresh you already do.
- **Internal:** renewal dates, low-usage campuses, upsell signals across accounts (valuable from ~10 accounts).

### Support Shield -> **"Research FAQ assistant"** -- Fit: **MODERATE**
- Answers "How do I get research credit?" or "What is SIRE?" from the office's own pages; escalates to advisors. Useful, but campus chatbots are becoming commodity. Bonus, not core.

### Proposal Machine -- Fit: **MODERATE (internal)**
- Generate founding-partner proposals, **HECVAT answers**, accessibility statements and budget-justification text per prospect. That saves real hours in a committee sale.
- Student-facing research-proposal drafting is **not recommended** (academic-integrity risk).

### Brand Clone -- Fit: **WEAK** (standalone) / folded into Outreach Coach
- Keep drafts in the **student's own voice** so emails don't read as AI-written. That's a feature of Outreach Coach, not a product.

### Content Atomizer -- Fit: **WEAK** (product) / moderate (internal GTM)
- Turn the NCUR talk and pilot report into LinkedIn posts and a newsletter. Internal only.

---

## Board Counsel (Craft & Execution)
> "Separate reversible decisions from irreversible ones and calibrate speed accordingly." -- Jeff Bezos, Craft & Execution Board (heading via `/sk-skills`)

**The Board's view:** shipping Outreach Coach is *reversible* (feature-flag it, cap volume, watch faculty reactions). Letting AI-written emails flood faculty inboxes under your brand is *not* (faculty trust is the supply side of this market). Move fast, behind guardrails, with faculty advisors watching.

---

## Step 3: Integration Recommendations (core / bonus / upsell)

| Skill (as Lab Atlas feature) | Could it be the core? | Bonus? | Upsell? | Decision |
|------------------------------|-----------------------|--------|---------|----------|
| Outreach Coach | Part of the core promise ("write to the right lab") | -- | Yes, as part of an Access Suite | **Upsell (Access Suite)**, pilot inside Emory first |
| Semester Impact Report | Needed for renewal | -- | Monthly/provost version | **Core** (semester report) + **Upsell** (monthly/provost dashboard) |
| Lab Radar | No | Yes (retention) | Part of the Access Suite | **Upsell (Access Suite)** |
| Research FAQ assistant | No | **Yes** | -- | **Bonus** in the Campus package |
| Proposal Machine | No | -- | -- | **Internal** (HECVAT, proposals) |
| Brand Clone | No | Folded into Outreach Coach | -- | Feature |
| Content Atomizer | No | -- | -- | **Internal** (GTM) |

## Step 4: Integration Plan
- **Primary recommendation:** build **Outreach Coach** first (behind guardrails), because it completes the "communication" half of your pitch and addresses the equity problem directly. Pilot it with one Emory cohort in Spring 2027 and measure faculty reply rates.
- **Bundle -- "Access Suite"** (Outreach Coach + Lab Radar + monthly impact dashboard): **+$8K/yr list** (+$4K founding).
- **Attraction angle:** the free **landscape snapshot** in the preview atlas is the Autopilot Report pointed at prospects.
- **Revenue projection:** if 30% of the ~16 institutions expected by FY2029 add the Access Suite at $8K, that's ~5 x $8K ≈ **$40K ARR** on top of core licenses. [Estimate]

## Step 5: Final Skills Matrix
| Skill | Fit | Role | Revenue potential | Priority |
|-------|:---:|------|-------------------|:---:|
| Outreach Engine (Outreach Coach) | Strong | Upsell (Access Suite) | Part of +$8K/yr per campus | **High** |
| Weekly Autopilot Report (Impact Report) | Strong | Core + Upsell | Retention driver; part of +$8K | **High** |
| Client Radar (Lab Radar + internal) | Strong | Upsell + Internal | Part of +$8K | Medium |
| Support Shield (FAQ assistant) | Moderate | Bonus | Included (Campus) | Low |
| Proposal Machine | Moderate | Internal | Saves ~10-20 hrs per deal [Estimate] | Medium |
| Brand Clone | Weak | Feature of Outreach Coach | -- | Low |
| Content Atomizer | Weak | Internal | -- | Low |

**First skill to build:** Outreach Coach (with guardrails), then Impact Report, since the report is what renews contracts.

## Red Flags
- **HECVAT 4 now includes AI-specific questions** (training data, model use, bias). [Data] Document which models are used, what student data is sent, retention (ideally none) and faculty-facing safeguards *before* shipping AI features to a customer.
- AI-drafted outreach that increases email volume would turn faculty (your supply) against the product.

## Yellow Flags
- Outreach drafts may contain student information. Keep drafting client-side or don't store it, to simplify FERPA review.

## Sources
- StartupKit skills catalog: `StartupKit-main/skills/sk-skills/references/skills-catalog.md`
- HECVAT 4 AI questions: https://campustechnology.com/articles/2025/02/11/educause-hecvat-vendor-assessment-tool-gets-an-upgrade.aspx?p=1
- Audit study: https://behavioralscientist.org/?p=7571
