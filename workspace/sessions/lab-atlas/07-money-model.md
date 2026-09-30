# Phase 7: Money Model -- Lab Atlas

> Session: `lab-atlas` | Generated: 2026-09-30 | Skill: `/sk-money`
> Inputs: `05-offer.md` (Every Lab in 45 Days; list $6K / $15K / $30K; founding 40-50% off), `03-competitors/pricing-landscape.md` (market ~$0-25K+; serviceable US pool ≈$12M/yr).
> Adaptation: StartupKit's money model is written for one-time coaching offers. Here "client" = institution, revenue is **annual recurring (ARR)**, and continuity is the default, not an add-on. All figures are **[Estimate]** unless marked [Data].

---

## Step 1: Core Pricing Math

| Item | Standard tier (≤3,000 investigators) | Research-university tier (≤10,000) |
|------|:---:|:---:|
| List price / yr | $15,000 | $30,000 |
| Founding price / yr (first 5, 2-yr term) | $8,000 | $15,000 |
| Annual fulfillment cost (hosting + CDN ~$1,000; data refresh + LLM classification ~$500; support ~20 hrs ≈ $1,000) | ~$2,500 | ~$3,500 |
| One-time onboarding cost (pipeline + QA ~40 hrs) | ~$2,000 | ~$3,000 |
| **Gross margin at list** | (15,000-2,500)/15,000 = **83%** | (30,000-3,500)/30,000 = **88%** |
| **Gross margin at founding price** | (8,000-2,500)/8,000 = **69%** | (15,000-3,500)/15,000 = **77%** |

Cost basis: ~$50/hr blended labor. **[Founder to confirm]** hosting choice and hours actually spent building v85's Emory data.

**Revenue targets (SaaS view):**
- $100K ARR = **7 institutions** at $15K (or 4 at $30K).
- $1M ARR = **67 institutions** at $15K (or ~40 at a $25K blended average with modules).
- StartupKit's one-time formula for reference: at $15K, $100K/yr needs 0.56 new institutions/month; $1M/yr needs 5.6/month. **Flag:** 5.6 new universities a month is unrealistic for a founder-led team. Recurring revenue plus module upsells is the only path to $1M.

**Lifetime value:**
- Assumed average lifetime **4 years** (annual renewals; institutional tools churn slowly once embedded, though early-stage vendors churn faster). [Assumption]
- LTV at list (Standard) = $15,000 x 4 x 83% = **$49,800**.
- LTV for a founding partner (2 yrs at $8K, then 2 yrs at $15K) = (2x8,000x69%) + (2x15,000x83%) = 11,040 + 24,900 = **$35,940**.

**Customer acquisition cost (founder-led):**
- Per won institution: ~4 preview atlases built (4 x ~$2,000 of time) + ~20 hrs of calls, demos and security reviews (~$1,000) + share of conference/travel (~$1,500) ≈ **$10,500**. [Estimate]
- **LTV:CAC ≈ 4.7 (list) / 3.4 (founding)**. Both clear the 3:1 bar, *if* previews convert at ~1 in 4. **Payback ≈ 10 months** at list (10,500 / (12,500/12)).

---

## Board Counsel (Value & Pricing + Market Focus)
> "Our final conclusions are always based on cost per customer." -- Claude Hopkins (via `/sk-validate`)

**The Board's view:** your economics hinge on one number nobody has measured: **how many preview atlases it takes to win one institution, and how many hours each preview costs.** Rockefeller-style cost discipline here means automating the preview pipeline (the "Atlas #2 in 14 days" test) before hiring anyone to sell.

---

## Step 2: Attraction Offers (pick 2)
1. **Free Goodwill: the Preview Atlas** *(primary)*. A private preview of the prospect's own campus from open data (publications, NIH/NSF awards, public directory), plus a 2-page **research-landscape snapshot** (bench-vs-computational mix by school, top collaboration clusters). Costs ~$2,000 of time; it's the most persuasive demo possible.
2. **Win Your Money Back: the Semester Pilot.** $2,500 for one cohort or one college for one semester, **credited in full** toward the first annual license if signed within 60 days of the pilot report.
- *(Also used)* **Pay Less Now or More Later:** founding pricing honored until **March 31, 2027**.

## Step 3: Upsell Offers
**Menu upsell (anchor with the top tier first):**
| Package | Includes | List / yr |
|---------|----------|:---:|
| **Campus** (anchor) | Discovery + Graduate module + Research Development module + annual landscape report + data API | $30K + modules ≈ **$48K** |
| **Plus** (target) | Discovery + Graduate module | Tier + $6K (e.g., **$21K** at Standard) |
| **Core** | Discovery only | Tier price ($15K Standard) |

**Classic upsells (modules):** Graduate Rotation & Recruitment (+$6K); Research-Landscape Report (+$5K; free the first year as a bonus); Faculty Collaboration Finder (+$8K); Data API/export to the institutional warehouse (+$4K); Outreach Coach (+$4K, roadmap).

**Rollover:** unused onboarding hours (e.g., adding a new school to the atlas) roll into the next year.

## Step 4: Downsell Offers
- **Feature/scope downsell:** Program or department license ($6K list / $3.5K founding) for one college, one graduate program or the medical school's research office when the central office can't buy.
- **Payment plan:** semester billing (2 x half) at no premium. Aligns with academic budgets.

## Step 5: Continuity Offers
- **Waived fee:** $2,500-5,000 onboarding waived on 2-year terms.
- **Continuity discount:** 3-year term = 10% off list, price locked (valuable when budgets are uncertain).
- **Continuity bonus:** monthly refresh (new faculty, new NIH awards: "labs likely expanding" alerts) plus an annual landscape report. The product literally gets more valuable every month.

---

## Step 6: Complete Money Model Summary

### Customer Journey Map
```
Preview Atlas (free)  -->  Semester Pilot ($2,500, credited)  -->  Annual License ($8-15K founding / $15-30K list)  -->  Modules (+$4-18K)  -->  Multi-year renewal (3-yr lock, -10%)
   ~30% -> pilot              ~60% -> annual                         ~30% add a module by year 2                        ~90% renew
```
Conversion rates are conservative guesses **[Assumption]** to be replaced with real data after the first 10 previews.

### Revenue per customer
- **Month 1** (founding Standard): $8,000 invoice (annual in advance) - $2,500 pilot credit = **$5,500 cash**
- **Year 1** (founding Standard + 1 module at founding rate $3,500): **~$11,500**
- **Break-even on acquisition cost:** ~month 10 at list; ~month 16 at founding pricing

### Growth scenario A: StartupKit monthly compounding
If you add **1 institution per month** at a $15K average ACV:
- Month 1 MRR: $1,250 -> Month 6: $7,500 -> **Month 12: $15,000 MRR ($180K ARR)**
- Year 1 cumulative revenue (recognized monthly): 1,250 x (1+2+...+12) = **$97,500**
- That's the "aha": even one new university a month compounds to $180K ARR in a year. But one a month is hard in higher-ed's 3-18-month cycles.

### Growth scenario B: realistic fiscal-year cohorts (university budgets run July-June)
| Fiscal year | New institutions | Cumulative | ARR at year end | Notes |
|-------------|:---:|:---:|:---:|-------|
| FY2027 (now -> Jun 2027) | Emory (design partner) + 1-2 pilots | 1-3 | ~$5-10K revenue | Pilot credits, maybe a landscape report |
| FY2028 | 5 founding partners (avg $11.5K) | 6 | **~$60-70K** | Includes pilots and reports |
| FY2029 | +10 at list (avg $17K incl. modules) | 16 | **~$230-270K** | Founding prices still locked |
| FY2030 | +20 | ~34 after churn | **~$550-650K** | Founding cohort rolls to list; ~10% churn of prior base |
| FY2031 | +25 | ~55 after churn | **~$1.0M** | Avg ~$18-19K with modules; requires a first sales hire in FY2029 |

### Year-1 costs (FY2027) and funding need
| Item | Estimate |
|------|:---:|
| Entity formation, IP counsel, contract templates | $5-15K |
| Accessibility audit + conformance report (VPAT/ACR) | $5-10K |
| Security: penetration test, policies, HECVAT prep | $5-10K |
| Insurance (general liability, cyber, E&O; universities commonly require certificates) | $2-5K |
| Hosting, tools, domains | ~$3K |
| Conferences and travel (NCUR, one regional UR meeting) | ~$8K |
| **Total (excluding founder pay)** | **≈ $28-51K** |

**Funding implication:** the first year is fundable **non-dilutively**: Emory Hatchery programs (the Sandbox advertises "$50,000+ in funding available"; Spring 2027 forms reopen in December), pitch competitions, the Emory design-partner fee, and pilot revenue. Only consider an equity round once FY2028 shows 5 paying institutions and repeatable onboarding. [Data + Opinion]

---

## Red Flags
- **Revenue concentration:** through FY2028 most revenue depends on Emory plus 5 founding partners. Losing one hurts. (Van Doren's warning in `02-niches.md`.)
- **Unmeasured CAC:** all unit economics assume ~1 in 4 previews convert. If it's 1 in 10, LTV:CAC drops below 2 and the model breaks.

## Yellow Flags
- Founding prices lock in low revenue for 2 years. Cap founding partners at 5.
- The core niche caps near **$12M/yr** of US spend (see `pricing-landscape.md`); $1M ARR ≈ 8% share. Achievable, but venture-scale returns need modules, adjacent buyers or international markets.
- Hours per onboarding are unknown until "Atlas #2 in 14 days" is run.

## Sources
- `05-offer.md`, `03-competitors/pricing-landscape.md`
- InfoReady PO (price anchor): https://sfasu.edu/application/procurement/contracts/B2400706.pdf
- Emory Hatchery programs: https://hatchery.emory.edu/programs/venture-support.html
- Budget cycles (Tier 3): https://www.getmonetizely.com/articles/how-do-edtech-saas-startups-align-with-educational-institution-budget-cycles
