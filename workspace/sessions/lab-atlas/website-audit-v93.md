# Website Audit: Emory Lab Atlas v93

> Session: `lab-atlas` | Audited: 2026-10-06 | Build: `Emory_Lab_Atlas_v93.html` (38.2 MB)
> Lens: **Marketing for Founders** (`Marketing-for-Founders-main.zip`, README sections in brackets) plus this session's positioning (`04-positioning.md`) and pitch scorecard (`10-pitch/pitch-scorecard.md`).
> Method: rendered in Chromium at 1440×900 (light and dark) and 390×844 (phone); scrolled every screen; walked all 7 app views with a real query; ran axe-core 4.10; checked the embedded data directly. Screenshots: `website-audit-v93/`.

**What's already strong** (keep it): honest provenance and error rates, the wet-to-dry axis as a visual identity, the "Bench or keyboard?" school breakdown, the new Past undergrad mentors view (293 professors with symposium evidence: the "takes undergrads" signal no competitor has), consent copy in My experience, no JavaScript errors, and only 3 moderate axe issues (duplicate banner/main landmarks).

---

## The 20 improvements, highest impact first

### Messaging and the first screen [Landing Pages, Messaging and Positioning]

**1. The hero doesn't say who it's for or what they get.**
MfF's test: a homepage must say *who* it's for, *what* it does, and *why* it's better. "Every lab at Emory, on one axis." does none of these for a first-year student; "axis" only makes sense after you've used the product.
*Fix:* lead with the student and the outcome, keep the axis as the visual. For example: **"Find an Emory lab that fits you, and know whether it's bench or computer work before you email."** Subhead: "Every investigator in 9 schools, from their papers and grants. Free for Emory students."

**2. The hero overclaims its own coverage.**
It says "7,078 investigators … placed between wet bench and dry computation." Inside the app, 5,395 are placed and 1,683 (24%) are unclassified. The product's credibility rests on honesty, so the first sentence shouldn't be the one inaccurate number.
*Fix:* "7,078 investigators; 5,395 placed on the axis."

**3. Make the search the hero action, not a button into another hero.**
"Enter the atlas" opens the Atlas view, which repeats the same headline ("Every lab at Emory, on one axis"). The "Ask the atlas" box, the thing students actually want, sits two screens down.
*Fix:* put the query box in the hero and send it straight to Find a lab results. Keep "Browse the atlas" as the secondary action. [Conversion Rate Optimization: the CTA should be the action, not "enter"]

**4. Add a path for the buyer, not just the student.**
There's no "Want this for your university?" anywhere, so a visiting undergraduate research director (your actual customer) has no next step.
*Fix:* a quiet footer block and a `/for-universities` section: what it is, a 2-minute walkthrough, "Request a preview of your campus" form (email capture). [Sales & Cold Outreach; Email Marketing]

### Things that look broken [Conversion Rate Optimization]

**5. Content is invisible at rest.**
The counting cards render "0 Investigators", "0 Departments & centres", "0 Placed on the axis", "0 Saved connections" until each scrolls into view, and long stretches render as empty navy or blank cards. Link previews, screenshots, slow phones and anyone with reduced motion see zeros.
*Fix:* write the real numbers into the HTML and animate *from* a visible state.

**6. "What the atlas is counting" overlaps itself on desktop.**
Sticky cards slide over the section heading, leaving fragments like "at the a / countin" (screenshot `03-counting-overlap.png`).
*Fix:* give the heading its own row or stop the cards before it.

**7. The first data visual wastes a full screen.**
The hero ridge chart is a flat line with one spike at the dry end, with axis labels too small to read (`02-hero-chart.png`). It says less than the donut further down ("11% wet, 1% hybrid, 63% dry, 24% unclassified").
*Fix:* swap them: the donut or a labelled 4-bar breakdown under the hero; move the ridge to the Atlas view.

**8. Two gates before any value.**
First entry opens a long methodology modal with a statistics table. My experience then needs a second "I understand" before the form unlocks. Each gate loses people.
*Fix:* one line under results ("Settings are predicted, about 1 in 12 is wrong. How we know →") and show the full note only when someone first clicks a setting. Keep the consent gate, but collapse it to two lines plus a "details" toggle.

### Search and data quality (the product's core promise)

**9. Search returns a firehose and matches filler words.**
"single-cell sequencing of tumors, hands-on bench work" returned **3,217 matches (45% of all investigators)**, and result chips show "hands" treated as a research term. Several top results are about renal carcinoma or thymoma.
*Fix:* stop words and phrase handling ("hands-on", "bench work", "computational" should set the setting filter, not match text); show the 140 strong matches by default with "show all"; show "matched because: single-cell, tumor" on each row.

**10. Confidence is high on thin evidence.**
898 placed records show ≥90% confidence while resting on at most one paper title and no grants. Example: an emeritus anesthesiologist shows **"Wet, 99%"** from one title (`06-profile-99pct.png`). A faculty member who sees that will distrust everything else.
*Fix:* cap confidence by evidence count, or show "based on 1 title" next to the percentage, and leave records under a minimum evidence bar unclassified.

### Trust, privacy and permission (these will block university sales)

**11. 798 student names are embedded and searchable.**
Past undergrad mentors includes student names and project titles from the symposium books ("Search: mentor, student, project"). The books are public, but a searchable index of students is the first thing a privacy or FERPA review will flag, and students with directory opt-outs can't be excluded.
*Fix:* keep mentor, year, program and a link to the source page; drop student names from the shipped data.

**12. Real faculty names and Emory buildings are used as decoration.**
The hero cards feature named faculty (e.g. Sarah Rezapourdan, Alberto Moreno, Elizabeth Head, Marie-Claude Perreault), and the "Bench or keyboard?" section uses photos of Emory buildings, plus the embedded Emory shield.
*Fix:* use illustrative or opt-in cards, your own photos or licensed ones, and plan the external name now (see `05-offer.md` pre-conditions on Emory name use).

**13. No privacy page, no "who made this", no contact.**
The form collects data and can sync to a server, but there's no privacy policy, no team, no endorsement, and no feedback link. [Landing Pages: social proof]
*Fix:* a short About ("Built by Emory students, supported by the Pathways Center" once they approve the wording), a plain-language privacy page, a feedback link, and 2-3 student quotes with consent.

**14. Use the proof you already have.**
"607 faculty have mentored 947 students at Emory's research symposia since 2007 (293 of them are in the atlas)" is strong, verifiable social proof, but they only appear deep inside one view. [Use Social Proof To Elevate Your GTM Efforts]
*Fix:* a proof strip on the landing page and a "Has mentored undergrads" badge in search results.

### Turning visits into outcomes

**15. The profile stops at an email address.**
The promise is facilitating student-to-PI communication, but a profile ends at an email link. The outreach tracker is buried in My experience.
*Fix:* a "Write to this lab" panel on every profile: one recent paper to mention, a short template, etiquette tips, "add to my tracker". [Sales & Cold Outreach: email templates]

**16. No measurement, so no traction to show.**
There's no analytics or event tracking. You can't say how many students searched, opened profiles or emailed, and traction was the weakest pitch score (4/10).
*Fix:* privacy-friendly analytics (self-hosted Plausible or Umami) with events for search, profile open, email click, star, tracker add and experience saved. Report weekly numbers. [Conversion Rate Optimization]

### Reach [SEO; LLM SEO, AEO, GEO; Free-Tool Marketing]

**17. Zero search and share footprint.**
No meta description, no Open Graph image (a link pasted into GroupMe or Slack shows nothing), no favicon, and all content is drawn by JavaScript from one data blob, so nothing is indexable.
*Fix:* basic meta and OG tags now. Later, static pages per department and topic ("Emory labs studying immunology: 38 bench, 12 computational"). That's programmatic SEO, and it's also what ChatGPT and Perplexity cite when a student asks "how do I find a lab at Emory?"

**18. Ship a free tool that works outside Emory.**
The wet/dry classifier is the most shareable thing you've built. MfF calls mini tools "10x more powerful than free trials."
*Fix:* "Bench or keyboard?": paste any lab's paper titles (or a PubMed author link) and get a setting with an explanation. Students at other schools use it, and it gives you a reason to talk to their research offices.

### Mobile and performance

**19. The phone experience is cramped and slow to start.**
On a 390×844 phone, the app's header, stats line, theme toggle and tabs take about a quarter of the screen. The landing page stacks roughly five screens of building photos. The graph is unusable at that width. "Hover a colour to compare" appears on touch screens.
*Fix:* compact header that collapses on scroll, horizontal strip for the school cards, a list fallback for the graph, touch-aware copy.

**20. 38 MB in one file.**
That's 10.9 MB gzipped, with a 150-190 MB JavaScript heap. It loads in about 2-3 s from local disk on a fast machine; on a phone over campus Wi-Fi or 4G it's a long blank wait, and it can't be cached per view.
*Fix:* ship the landing page separately (under 500 KB) and load the data per view as JSON (the server you added in v93 can serve it).

---

## Copy polish (small, quick)
- US spelling for a US audience: "tumours" is in a landing-page example chip; "programme(s)" appears 370 times in the build, including the "Programmes" filter; "centre" appears 27 times.
- Jargon students see: "Community k>=3", "P(wet) = 0.99", "BCDB / CB / GMB …" without names, and "Inactive / emeritus" next to "Emeritus".
- Remove the code comments referencing another company's homepage ("as on Think's homepage", 6 occurrences) before sharing the source.
- Accessibility: fix the duplicate `banner`/`main` landmarks flagged by axe (landing nav and app masthead both present).

## Suggested order
1. This week: items 2, 5, 6, 11, 17 (accuracy, broken rendering, student names, meta tags).
2. Before the Emory pilot: 1, 3, 8, 9, 10, 13, 15, 16.
3. Before selling to other universities: 4, 12, 14, 18, 19, 20.

## Sources
- Marketing for Founders README (`Marketing-for-Founders-main.zip`): sections Landing Pages, Messaging and Positioning; Conversion Rate Optimization; SEO; LLM SEO/AEO/GEO; Free-Tool Marketing; Sales & Cold Outreach; Email Marketing.
- Rendered audit of `Emory_Lab_Atlas_v93.html` (Chromium via Playwright, axe-core 4.10.2); figures from the embedded `atlasdata` and `surehist` blocks.
