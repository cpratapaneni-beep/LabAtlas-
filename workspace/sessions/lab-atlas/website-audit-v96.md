# Website Audit: Emory Lab Atlas v96

> Session: `lab-atlas` | Audited: 2026-10-06 | Build: `Emory_Lab_Atlas_v96.html` (38.3 MB)
> Lens: the repo's `anti-ui-slop` skill (audit, polish and distill playbooks: "distinction should come from the product's content, structure, typography… not from novelty"; "use motion only to explain a transition"; "remove decorative noise that competes with the task"), plus the Marketing for Founders lens from the v93 audit.
> Method: same as v93. Chromium at 1440×900 (light, dark) and 390×844; every landing screen; all 7 app views with a real query; axe-core 4.10; computed-style probes; embedded data checked. Screenshots in `website-audit-v96/`.

## What v96 fixed from the v93 list
- Headline now says who it's for and what they get; coverage is stated honestly (5,170 placed, the rest "too little on record").
- Search is the hero action. "hands-on bench work" now becomes a filter (78 strong matches instead of 3,217), with "matched on" terms.
- Confidence is capped on thin evidence: 0 records now show ≥90% on ≤1 title (was 898). A. Allen III dropped from 99% to 65% "low confidence".
- Student names removed from the shipped mentor data (0 of 954 records).
- Methodology modal replaced by a one-line banner with "How we know".
- Meta description, Open Graph tags and a favicon added; US spelling; touch-aware copy; a list fallback for the graph on phones.
- Proof strip ("608 faculty have mentored 949 undergraduates"), "Mentored undergrads" badges in results, "independent student project" disclaimer, About and Privacy.

axe-core reports one moderate issue (heading order) and no JavaScript errors. The problems below are what a person sees.

---

## The 20 critiques, highest impact first

### Broken on screen

**1. The closing call to action has no visible label.**
"Browse the atlas" renders navy text (`rgb(3,27,54)`) on a navy pill, so it shows as a blank pill with an arrow on desktop and phone (`01-cta-invisible-label.png`). It's the last action on the page.
*Fix:* light text on the pill, or a light pill.

**2. Footer links are invisible, and the buyer path is switched off.**
"About" and "Privacy" are navy on the navy footer (`02-footer-invisible-links.png`). "Contact", "For universities" and the "Want this for your campus?" form are hidden because the contact setting is empty, so a visiting research director still has no way to reach you.
*Fix:* fix the link color; set the contact email or endpoint so the form and links appear.

### What reads as AI-generated, and what to do instead

**3. The halftone dot field runs through the text.**
The dot texture sits behind the subhead, the example chips and the body paragraph, and dots cross the letters (`03-hero-halftone.png`). Ambient dot or grain fields are one of the most common generated-site backgrounds right now, and here it's pure decoration.
*Fix:* make the texture the data. Draw one dot per investigator, colored by setting (5,170 placed dots plus grey for unclassified), and keep it out from behind text. Then the background says "every lab at Emory" instead of "template".

**4. The copy leans on two-beat slogans.**
"Useful, not definitive." "Titles in, a setting out." "Seven views, one field." "Every lab, read from what it publishes." "One box, one answer: the refinements beside it are optional and none of them is asked twice." "Somewhere in here is your next lab." Balanced aphorisms like these are the most recognizable machine-writing pattern, and none of them tells a student what to do.
*Fix:* replace each with a specific statement or an action. Examples: "About 1 in 12 settings is wrong; check the lab's recent papers." "Search 7,078 investigators by what you want to work on."

**5. Everything is uppercase monospace.**
There are 90 uppercase rules: buttons, chips, section titles ("READ THE FIELD"), links, and even body paragraphs in the 01-04 cards are set in mono. The terminal look is a generated-site default, and all-caps example queries ("SINGLE-CELL SEQUENCING OF TUMORS") are harder to read and copy.
*Fix:* sentence case for buttons, chips and links. Use mono only for numbers and data labels.

**6. Six typefaces.**
Inter, Instrument Sans, Archivo Narrow, Newsreader, Space Mono and IBM Plex Mono, including two monospaces and a serif used only for one-line slogans. That's why sections feel like they came from different sites.
*Fix:* one sans for text and headings, one mono for data. Drop the condensed caps and the second mono.

**7. The landing page and the app look like two products.**
The landing is cream halftone with condensed caps. The app is Instrument Sans with building photos and its own hero ("The whole field, bench to computer."). The accent is blue in light mode, gold in dark mode, plus cyan and green elsewhere (`04-hero-dark-gold.png`).
*Fix:* one accent color in both themes and one type system. Drop the second hero inside the app and land people on the results or map.

**8. The same numbers repeat.**
7,078 appears in the hero paragraph, the stat strip, the donut and the counting tiles, and again in the app header and app hero. Wet/hybrid/dry shares appear three times in three different chart styles. Repetition reads as padding.
*Fix:* state each fact once, where it's used; keep one breakdown chart.

**9. The numbered 01-04 card stack is a template pattern.**
Sticky numbered panels, rows of tag pills ("ATLAS · WET TO DRY · NINE SCHOOLS · EVERY DEPARTMENT"), and a square button with a separate arrow box (`06-numbered-stack.png`). The pills are labels, not information.
*Fix:* show one real artifact per view instead: an actual result row with its "Mentored undergrads" badge, an actual profile with its setting and evidence. Real product screens are the strongest proof you have.

**10. The 3D glowing network explains nothing.**
"Every connection, in three dimensions. Schools glow at the surface…" (`07-3d-network.png`). A rotating particle cloud with glows can't be read, and the app already has a working 2D graph.
*Fix:* cut it, or show one concrete path: "Prof. A → co-authored with Prof. B → shares a grant with Prof. C", with the real names opt-in.

**11. Ornament without meaning.**
A scrolling marquee ("My experience · kept in this browser only"), a dotted halo around the closing button, corner tick marks on the footer frame, gradient-filled text on the word "computer.", glows, and 13 backdrop blurs. The anti-ui-slop rule applies: motion and ornament only when they explain something.
*Fix:* keep the wet-to-dry gradient only where it encodes data (the axis), and remove the rest.

**12. Building photos stand in for labs.**
Nine Emory building photos, now in a "Drag or scroll" carousel plus the school cards. Buildings don't tell a student anything about a lab, and they lean on Emory's brand.
*Fix:* real lab photos taken with permission, or no photos; let the map and data carry the imagery.

**13. The giant "EMORY LAB ATLAS" footer wordmark.**
The oversized framed wordmark is a current template trend, and it puts the Emory name in the largest type on the page, right above "Not an official Emory University service".
*Fix:* a normal-size footer; plan the non-Emory product name (see `05-offer.md`).

### Layout and length

**14. Empty and half-empty screens.**
One full desktop screen holds only dots and "Every lab, read from what it publishes." (`05-empty-screen.png`). The rotating line "Before you write, know whether the work is… a mix of both" is clipped at the top as it scrolls. "A note on the map" in the counting section is still an empty card.
*Fix:* remove the interstitial screens; fill or cut the empty card.

**15. The phone page got longer.**
It's now 13,081 px tall (about 15 screens), up from 9,134 px in v93 (`08-phone-landing.png`).
*Fix:* on phones keep the hero search, one breakdown, the mentor proof, three view previews and the footer; drop the photo carousel, 3D network and marquee.

### Details

**16. The preview image isn't shipped.**
`og:image` points to `og-image.png`, but the build contains only the HTML file, so link previews will show no image unless that file is deployed beside it.
*Fix:* deploy the PNG with the page, or use an absolute URL.

**17. Search shows word stems.**
"Matched on: single · cell · sequencing · tumo".
*Fix:* show the word the user typed ("tumors").

**18. Analytics is wired but off.**
Plausible/Umami support exists but does nothing until an endpoint is set, so you still have no usage numbers for the pilot or the pitch.
*Fix:* set the endpoint before the Emory pilot.

**19. 27% of investigators have no setting.**
Unclassified grew from 1,683 to 1,908, more than one in four. The honesty is right, but those rows are dead ends.
*Fix:* on each, show what is known (department, papers) and a "Know this lab? Tell us bench or computer" prompt that feeds the human-check set.

**20. Still 38 MB in one file.**
Load is about 3 s from local disk with a 130-160 MB JavaScript heap; much slower on a phone network.
*Fix:* ship the landing page separately and load data per view (unchanged from v93 #20).

---

## The principle behind most of these
Every decorative element should carry real information from the atlas. The dots are investigators, the gradient is the wet-to-dry axis, the images are real labs, and the copy names a number or an action. Anything that could appear unchanged on another startup's landing page (dot fields, glows, marquees, numbered stacks, 3D clouds, aphorisms) is what makes a site read as generated.

## Suggested order
1. Today: #1, #2, #16 (invisible labels, hidden buyer path, preview image).
2. This week, the de-slop pass: #3, #4, #5, #6, #11, #14 (one change set: type, copy, texture, ornament).
3. Before the Emory pilot: #7, #8, #9, #10, #15, #17, #18.
4. Later: #12, #13, #19, #20.

## Sources
- `anti-ui-slop` skill (`anti-ui-slop.zip`): SKILL.md, reference/audit.md, reference/polish.md, reference/distill.md, reference/new-work.md.
- `taste-skill-main.zip` redesign-skill anti-pattern list (AI copywriting clichés, generic card and button patterns).
- Rendered audit of `Emory_Lab_Atlas_v96.html` (Chromium via Playwright; axe-core 4.10.2); figures from the embedded `atlasdata` and `surehist` blocks.
