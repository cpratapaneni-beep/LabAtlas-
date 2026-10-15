# Future directions: other universities, and a pipeline that runs itself

Two questions:

1. How would the same atlas, with this exact layout, be made for a university
   other than Emory, without rebuilding it by hand each time?
2. How would the scraping be automated, so the site repopulates itself instead
   of somebody running each script?

Both have the same answer at their core. Make the page a **template** that knows
nothing about Emory. Make each university a **config file plus a set of source
adapters**. Then have a **scheduled pipeline** fetch, check, build and publish
each site, with a person approving any change that looks wrong.

---

## Where things stand

| Part | Today | Emory-specific? |
| --- | --- | --- |
| Page code | `part_head.html` (CSS and markup) plus `part_tail.html` (script), spliced around one JSON block, `<script id="atlasdata">` | Partly: see the inventory below |
| Data | One JSON object: `insts`, `depts`, `pis` (7,078), `grants`, `pubs`, `vocab`, `gdbbs`, `wd` | The *content* is; the *shape* is not |
| Base investigator list | Came from an earlier scrape of Emory's own directories; **no scraper for it lives in this repo** | Yes, and it is the biggest gap |
| NIH funding | `scripts/nih_reporter_verify.py`, against the public RePORTER API | No: RePORTER covers every US institution |
| Wet/dry model | `ml/wetdry.py`, trained on Emory gold labels from publication titles, profile text and grants | The model transfers; the calibration has to be measured per school |
| Graduate programmes | `scripts/gdbbs_scrape.py` and the browser collectors, read from biomed.emory.edu | Yes |
| Build | `scripts/build_atlas.sh source.html out.html` | Assumes one source file |
| Human inputs | `ml/lab_corrections.csv`, `ml/gold_labels*.csv`, the monthly "My experience" responses | Per school |

### What in the page is Emory-specific

This is a short list, which is what makes the template approach cheap:

- About a dozen strings in the script: the Emory unit names in comments and
  copy, "Emory College", "Emory directory", and so on.
- The **GDBBS programme table** (`GD_PROGRAMS`: BCDB, MMG, IMP…), which is
  hard-coded.
- The **PHOTOS manifest**, keyed by Emory unit codes (SOM, CHOA, Winship…).
- The **shield image**, the wordmark "Emory Lab Atlas", `<title>`, and the
  landing headline ("Every lab at Emory, on one axis").
- The landing's numbers are already computed from the data, never typed, so
  they carry over for free.

---

## 1. One template, many universities

### 1a. Move identity into a `site` block in the data

Add one object to the data JSON and have the page read everything
university-specific from it:

```json
"site": {
  "slug": "emory",
  "name": "Emory University",
  "short": "Emory",
  "domain": "emory.edu",
  "wordmark": "Emory Lab Atlas",
  "logo": "data:image/png;base64,…",
  "units": [{"k": "SOM", "label": "School of Medicine"}, …],
  "grad_programs": {"BCDB": "Biochemistry, Cell and Developmental Biology", …},
  "grad_label": "GDBBS",
  "photos": {"units": {…}, "landing": {…}},
  "accent": {"light": "#283f7d", "dark": "#ec633d"}
}
```

The template then contains no institution names at all. A test that greps the
built page for "Emory" when building a non-Emory site catches any string that
was missed.

### 1b. A config folder per university

```
sites/
  emory/
    site.yaml            # the identity block above, in YAML
    sources.yaml         # where each kind of record comes from (see 1c)
    corrections.csv      # lab_corrections for this school
    gold_labels.csv      # hand labels for measuring the model here
    photos/              # landing and unit photographs
  gatech/
    …
```

`sources.yaml` names the university in identifiers the open databases already
use, so most of the data needs no scraper at all:

```yaml
ror: https://ror.org/03czfpz43          # Emory's ROR ID; OpenAlex and ORCID resolve institutions from it
nih_reporter_orgs: ["EMORY UNIVERSITY"]  # org names as RePORTER spells them
directories:                             # the university's own faculty listings
  - adapter: html_list                   # a generic parser, configured by selectors
    url: https://med.emory.edu/departments/…/faculty
    unit: SOM
    selectors: {card: ".faculty-card", name: "h3", title: ".title", email: "a[href^=mailto]"}
  - adapter: playwright                  # for listings built in JavaScript
    url: …
grad_programs:
  adapter: gdbbs                         # today's scraper, generalised
  base: https://biomed.emory.edu
```

### 1c. Get the data from sources that cover every university first

The order matters, because per-site scrapers are the part that breaks:

1. **OpenAlex** (open data, covering any institution by its ROR ID). It now
   asks for a free API key, which has its own daily budget. It gives authors whose last known affiliation is the institution, their works
   and topics. The wet/dry model reads publication titles, so this one source
   feeds most of what the model needs.
2. **NIH RePORTER** (public API, already used by `nih_reporter_verify.py`):
   active awards by organisation name, for any US institution. Add the **NSF
   Awards API** the same way for NSF-heavy schools.
3. **ORCID**, to settle names and affiliations when OpenAlex is unsure.
4. **The university's own directories**, only for what the open sources cannot
   say: who is currently *faculty*, their department and title, emeritus
   status, and graduate-programme membership. These are the per-site adapters.
   Most can be a generic HTML-list parser configured by CSS selectors. The rest
   need Playwright, which `gdbbs_scrape.py --browser` already uses.

The adapters all write the same **canonical record**, validated by a JSON
Schema before anything is built:

```
Person { name, units[], departments[], degrees, email, profile_url,
         description, status, publications[], grants[], sources[] }
```

Joining the sources (directory person ↔ OpenAlex author ↔ RePORTER PI) reuses
the name matching the GDBBS layer already does: surname plus first name or
initial, email when present, and ambiguous forms struck out rather than
guessed. OpenAlex and ORCID IDs make it much stronger.

### 1d. The model on a new campus

The wet/dry classifier learns from publication titles, profile text and grants.
That transfers between universities, but its accuracy has to be measured again
before a new site is published, never assumed:

- Label about 150 investigators at the new school with the existing tools
  (`ml/make_human_check.py` builds the blind workbook, and
  `LABELLING_RUBRIC.md` is the rubric).
- Run `ml/wetdry.py evaluate` against them. Publish the per-school accuracy on
  the page, as the Emory numbers are published now.
- Map the new school's departments onto the department types in
  `ml/department_types.csv`. This is a one-off per school, mostly by name.

### 1e. Build and host

```bash
python3 scripts/build_site.py --site sites/gatech --out dist/gatech/index.html
```

`build_site.py` would replace `build_atlas.sh`: read the config, run the
adapters (or load their cached output), clean, verify NIH, predict, audit,
then splice the template around the data.

Hosting as static pages (GitHub Pages, Cloudflare Pages or Netlify) at
`/emory/`, `/gatech/` and so on costs nothing. For the web, the 37 MB page
should load its data as a separate gzipped file (roughly a quarter of the size)
instead of inlining it. The single self-contained HTML can stay as the offline
download.

---

## 2. A pipeline that repopulates itself

### 2a. What runs, and in what order

A scheduled job, monthly (the "My experience" page already promises a monthly
update), for each site in `sites/`:

1. **Fetch.** Run every adapter. Keep the raw responses in a dated snapshot
   (`snapshots/<site>/<date>/`), so any build can be reproduced and a bad
   parse can be diagnosed without fetching again.
2. **Normalise and validate.** Produce canonical records and check them against
   the schema.
3. **Compare with last month.** Write a diff report: investigators added and
   removed, title and department changes, grants started and ended, and
   classifier calls that flipped.
4. **Guard rails.** Stop the run instead of publishing if:
   - any source returns zero records, or drops more than about 10% from last
     month (the page markup changed, or the site blocked the request);
   - `audit_atlas.py` reports errors (it already exits non-zero);
   - the model's measured accuracy on the gold set falls below its floor.
5. **Build** with the current model. Retraining stays a deliberate, reviewed
   step; it is not part of the monthly run.
6. **Merge human inputs:** `corrections.csv`, gold labels, and that month's
   experience responses.
7. **Propose, don't push.** Open a pull request with the new HTML and the diff
   report as its description. A person reads the diff and merges it; the merge
   publishes the site. A run that stayed inside the guard rails could
   auto-merge once the pipeline has earned trust.

### 2b. An example workflow

This is a sketch to adapt; it is not active. It would live at
`.github/workflows/refresh.yml`:

```yaml
name: Refresh atlases
on:
  schedule: [{cron: "17 6 1 * *"}]   # 06:17 UTC on the 1st of each month
  workflow_dispatch: {}               # and on demand
jobs:
  refresh:
    runs-on: ubuntu-latest            # or self-hosted, see 2c
    strategy: {matrix: {site: [emory]}, fail-fast: false}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -r requirements.txt && python -m playwright install chromium
      - run: python3 scripts/build_site.py --site sites/${{ matrix.site }} --fetch
               --snapshot snapshots/${{ matrix.site }} --out dist/${{ matrix.site }}/index.html
               --diff build/${{ matrix.site }}-diff.md
        env:
          OPENALEX_API_KEY: ${{ secrets.OPENALEX_API_KEY }}   # free key from openalex.org
      - uses: peter-evans/create-pull-request@v6
        with:
          branch: refresh/${{ matrix.site }}
          title: "Monthly refresh: ${{ matrix.site }}"
          body-path: build/${{ matrix.site }}-diff.md
```

### 2c. Things that will come up

- **Blocked requests.** University sites sometimes refuse requests from cloud
  IP ranges, or build their listings in JavaScript. Playwright handles the
  second. For the first, run the job on a self-hosted runner inside the
  university network, or keep using the browser collectors
  (`scripts/collect_gdbbs.js`) for that source and commit their output.
- **Keys.** NIH RePORTER and ROR need none. OpenAlex needs a free key, stored
  as a repository secret, never in the config.
- **Scraping politely.** Respect `robots.txt`, send an identifying User-Agent
  with a contact address, rate-limit, and use `ETag`/`If-Modified-Since` so
  unchanged pages are not downloaded again.
- **Experience responses.** Today they are downloaded by hand from the page.
  Replace that with a small form backend (a Google Form/Sheet, or a serverless
  endpoint) that the pipeline reads at step 6.
- **Freshness on the page.** Every layer already shows when it was read
  (`generated` dates). Also show the date of the last successful refresh in the
  masthead, so a stale site is visible to its readers.
- **Alerts.** A failed or guard-railed run notifies the maintainers, and the
  site keeps last month's version rather than publishing a broken one.

---

## Suggested order of work

1. Pull the Emory identity out of the page into `site` (1a), and add the
   "no stray Emory" build check. The page is then a template.
2. Write the canonical schema, plus an **Emory directory adapter**, so the base
   investigator list can be rebuilt from source. This is the missing piece
   today.
3. Add the OpenAlex adapter, and check it against the existing Emory
   publication data. This decides how much per-site scraping any future school
   needs.
4. Wrap the existing steps in `build_site.py`, with snapshots and the diff
   report.
5. Put it on a monthly schedule, opening pull requests (2b).
6. Pilot a second university: config, adapters, about 150 gold labels, and a
   measured model.
