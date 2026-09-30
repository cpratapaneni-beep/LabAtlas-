# Competitive Feature Matrix: Lab Atlas
*Skill: sk-competitors | Generated: 2026-09-30*

Rating scale: **Strong / Adequate / Weak / Missing / Unknown**. Lab Atlas is rated on **v85 as it exists today**, not the roadmap.

## Feature Comparison
| Feature | Lab Atlas v85 | ForagerOne | Handshake | Homegrown (PairMe etc.) | Profile systems (Pure/Elements/Profiles RNS) | AI assistants | Status quo |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Coverage with **zero faculty effort** | Strong (7,078 from records) | Adequate (auto-created, then claimed) | Missing (posted roles only) | Missing (posted roles only) | Strong (faculty with pubs) | Adequate (web crawl) | Weak |
| Evidence depth (publications, grants) | Strong (114,547 pub records; NIH layer) | Unknown | Missing | Missing | Strong | Adequate | Weak |
| **Method classification (wet / hybrid / dry)** | Strong (91.6% test accuracy; hybrid weak) | Missing | Missing | Missing | Missing | Weak (ad hoc) | Missing |
| Plain-language matching | Strong (related terms, typo tolerance) | Unknown | Adequate | Weak | Adequate | Strong | Missing |
| Collaboration graph | Strong (co-author, grant, topic; 3 degrees) | Unknown | Missing | Missing | Adequate-Strong (Profiles RNS networks) | Missing | Missing |
| "Takes undergrads" / availability signal | Weak (local "My experience"; GDBBS flags empty) | Adequate (faculty toggle; upkeep-dependent) | Strong (for posted roles) | Strong (for posted roles) | Missing | Missing | Weak (word of mouth) |
| Postings & applications workflow | Missing | Strong | Strong | Adequate | Missing | Missing | Missing |
| Student-to-PI messaging / outreach help | Weak (shows email) | Strong (messenger to email) | Adequate | Adequate | Missing | Adequate (drafts emails) | Weak |
| Admin analytics & outcomes | Missing (monthly CSV export) | Strong (claims "actionable analytics") | Strong | Unknown | Adequate | Missing | Missing |
| Enterprise readiness (SSO, HECVAT, VPAT) | Missing | Strong (SSO documented) | Strong | Adequate (campus login) | Strong | Adequate (Edu tiers) | -- |
| Research symposium tooling | Missing | Strong (Symposium) | Missing | Missing | Missing | Missing | -- |
| Provenance & error disclosure | Strong (published accuracy, caveats) | Unknown | Weak | Unknown | Adequate | Weak | -- |
| Multi-institution onboarding speed | Weak (Emory-specific pipeline) | Strong (200+ launched) | Strong | Missing | Adequate | Strong | -- |
| Works offline / no install | Strong (single file) | Missing | Missing | Missing | Missing | Missing | -- |

## Gap Analysis
Features where **no competitor excels**:
- **Method classification.** Nobody tells a student whether a lab works at the bench or the keyboard. Lab Atlas's clearest unique asset.
- **Verified "took undergrads recently" data.** Everyone has either nothing or a self-reported toggle. A compounding data moat is available.
- **Equitable outreach coaching.** Nobody helps students write a credible, well-targeted first email (the documented bias point) or protects faculty from untargeted volume.
- **Outcome and equity analytics tied to discovery.** ForagerOne has analytics, but its discovery is limited to what faculty publish on it.

## Differentiation Opportunities
1. **"Every lab, no faculty effort, with evidence."** Lead with coverage plus the wet/dry spectrum plus grants and publications. Most defensible in medical-center universities.
2. **A placement record.** Turn "My experience" into verified, advisor-confirmed placements. Show "took undergrads in the last 12 months" and route students toward labs that actually say yes.
3. **Outreach coach with guardrails.** Evidence-grounded first emails, etiquette coaching for first-gen students, weekly send limits, and respect for faculty "not taking students" flags. Fewer, better emails for faculty.
4. **Integrate, don't duplicate.** Deep-link each profile to the institution's ForagerOne or Handshake record so the transaction stays where the office already works.

## Red Flags
- Lab Atlas rates **Missing** on four procurement-critical rows (workflow, analytics, enterprise readiness, multi-institution onboarding). Buyers score these first.

## Yellow Flags
- Several ForagerOne cells are **Unknown** because its product site couldn't be fetched (JS-rendered). Get a demo or a customer walkthrough before finalizing battle cards.

## Sources
See `competitors-report.md` Sources; v85 figures come from the embedded dataset (generated 2026-09-29).
