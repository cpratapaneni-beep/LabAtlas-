# Marking GDBBS graduate faculty in the atlas

The atlas can show, on every row and every profile, which of Emory's GDBBS PhD
programs an investigator takes graduate students through — BCDB, CB, GMB, IMP,
MMG, MSP, NS, PBEE and the rest — and which of them the program rosters list as
currently accepting students.

None of that is in the atlas's source data, and none of it can be inferred from
a lab description, so it is read from the programs' own faculty directories on
`biomed.emory.edu`. Until that has been run the whole layer stays inert: no
badge, no filter, and no claim either way about anybody. A marking that was
guessed at would be worse than no marking, on a page people use to decide who
to write to.

## Two ways to get one

The roster is part of the atlas file: it is written into the page when the page
is built, and the page itself has no way to load one afterwards. Both routes
below end with the roster inside a new copy of the HTML.

### 1. From your own browser — no install (easiest)

The program directories are all on one origin, so a snippet running on any page
of `biomed.emory.edu` may read every other page of it. No Python, no extension,
no CORS.

1. Open <https://biomed.emory.edu/about-us/faculty-search.html>
2. Open the console — F12, or Cmd-Option-J / Ctrl-Shift-J
3. Paste the whole of `scripts/collect_gdbbs.js` in, press Enter
4. Run `await GDBBS.all()`

It reads each program's directory, prints what it found per program, and
downloads `gdbbs.json`. A directory that builds its list in JavaScript is
rendered in a hidden same-origin frame and read from there, so that case is
handled too.

If a program still comes back empty, open it yourself, scroll to the bottom so
every entry has rendered, and run `GDBBS.here('MMG')` — results accumulate
across pages. Then `GDBBS.save()`.

Write the file into the atlas:

```bash
python3 scripts/gdbbs_scrape.py --from-json gdbbs.json \
    --atlas Emory_Lab_Atlas_v97.html --out Emory_Lab_Atlas_v98.html
```

### 2. From a machine that can reach the site

```bash
pip install agent-reach          # or: --agent-reach /path/to/Agent-Reach-main

python3 scripts/gdbbs_scrape.py \
    --atlas Emory_Lab_Atlas_v64.html \
    --out   Emory_Lab_Atlas_v65.html
```

This one writes the roster into the HTML itself, which is what you want if the
file is going to be handed to other people. It prints, per program, how many
names it found and which URL they came from, then how many of those it could tie
to a record. Open `gdbbs.json` and read a few entries before trusting a run: if
a program's count is 0, or the names look like headings rather than people, the
markup has moved and the parser needs a look.

`gdbbs.json` from either route works in the other: the script applies a
collector file with `--from-json`.

(Until v85 the atlas also had a panel under Notes for loading a roster file or
pasting a directory page into the open page. It was removed in v86; a roster now
only arrives through the build, so every copy of the file says the same thing.)

## Options

| flag | what it does |
| --- | --- |
| `--agent-reach PATH` | import Agent Reach from a checkout instead of site-packages |
| `--browser` | render each directory with Playwright first — use when a program's list is built in JavaScript and the plain fetch comes back empty |
| `--only BCDB MMG` | read just these programs |
| `--json PATH` | where to write the roster on its own (default `gdbbs.json`) |
| `--from-json PATH` | skip fetching; patch the atlas from a roster read earlier |
| `--atlas` / `--out` | the atlas to read, and where to write the marked copy |

`--from-json` is the one to use when the page markup has beaten the parser: fix
`gdbbs.json` by hand, then apply it without fetching anything again.

## How it reads a page

1. **Agent Reach** (`agent_reach.channels.web.WebChannel`) reads the URL through
   Jina Reader and returns Markdown — easier to parse than the page source, and
   less likely to be refused.
2. **Playwright** with `--browser`, which renders the page, clicks through any
   "load more" pagination, and reads the DOM.
3. **urllib**, as a plain fallback.

Names are taken from lines that look like a person and not like a heading or a
job title, in either `First Last` or `Last, First` order. A line's own few
following lines decide the students flag: `accepting students` sets it, `not
currently accepting` clears it, and a page that says nothing either way leaves
it unset, which the atlas renders as GDBBS faculty with no claim about students.

## How a name is matched to a record

Three forms, strict to loose: the full normalised name, first plus last, and
first initial plus last. A form that two roster entries share, or that two
records in the atlas share, is struck out rather than resolved by whichever was
read first — `M. Aaron` is both Maria and Michael. The page applies exactly the
same rule, so the count the script reports is the count the page shows.

## What lands in the file

One key, `gdbbs`, inside the atlas's existing data block:

```json
{"generated": "2026-09-21",
 "source": "https://biomed.emory.edu",
 "programs": {"BCDB": "Biochemistry, Cell and Developmental Biology", "...": "..."},
 "people": {"Victor Corces": {"p": ["BCDB", "GMB"], "a": true,
                              "u": "https://biomed.emory.edu/PROGRAM_SITES/BCDB/about-us/faculty-search.html"}}}
```

`p` are the program codes, `a` is whether the roster says they are accepting
students, `u` is the directory the entry was read from. Nothing else in the
file is touched.

## A standing caveat

A roster is a snapshot, and program pages go stale between admissions cycles.
The atlas says so on the profile and in the Notes view. Confirm with the
program or the lab before relying on it.

# Checking and rebuilding the data

| script | what it does |
|---|---|
| `audit_atlas.py atlas.html [--out dir]` | checks every record for errors that can be proved from the file alone (grant counts and dollars that disagree, cut-off grant titles, duplicate papers, one PMID under two titles, broken co-author links, fused degrees, shared boilerplate bios, bad emails); exits non-zero on any error and lists the rest for review |
| `clean_atlas_data.py in.html out.html [--log dir]` | fixes what can be fixed with certainty and logs every change; nothing it does rests on a guess |
| `nih_reporter_verify.py atlas.html --patch` | re-reads every Emory award from NIH RePORTER, matches the PIs to atlas people and writes `atlas_nih.html` with verified figures and per-award links. It needs internet access to `api.reporter.nih.gov`; `--selftest` runs its checks offline |
| `build_atlas.sh source.html out.html [--no-nih]` | all of it in order: clean, verify NIH, run the wet/dry model (see `ml/README.md`), audit |
| `landing_images.py atlas.html photos/ -o out.html` | puts photographs into the landing page's image slots from files named after them (`hero-1.jpg`, `note-method.png`, ...), embedded so the atlas stays one file; `--list` prints every slot and the size it is drawn at |

Only RePORTER can settle the NIH grant figures. Until `nih_reporter_verify.py`
has been run from a machine that can reach it, the audit will keep listing
those as errors, and the page says the figures are unverified.

# Past undergrad mentors (symposium abstract books)

The "Past undergrad mentors" view, and the symposium record on each profile,
come from the abstract books of Emory's undergraduate research symposia (SURE in
summer, URP / SIRE in spring and fall). `scripts/symposium_scrape.py` rebuilds
that data and can write it straight into the page:

```bash
python3 scripts/symposium_scrape.py --atlas Emory_Lab_Atlas_v97.html \
    --cache build/symposia --fetch \
    --out build/surehist.json --report build/symposium_report.md \
    --write-atlas
```

- **Read from the books themselves** (`--fetch` downloads them from
  college.emory.edu): the Summer 2021 abstract book, the Spring 2026
  abstracts, and the Summer symposium page. That page is rewritten each year,
  and the script reads the year from it. Each project gives its student,
  title, faculty mentor and page.
- **2007–2019** exist only as Issuu editions, which do not serve scripts, so
  those records are taken from the page's earlier extraction and every mentor
  name is checked before it is kept:
  - department, facility and sentence fragments are dropped;
  - names run into other text are recovered ("Religion Diannestewart" → Dianne Stewart);
  - co-authors listed beside the real faculty mentor are dropped;
  - names that are the presenting student are dropped.
- Mentors are matched to atlas investigators by name: exact, then nicknames,
  then one-letter slips. A match only counts when it is unique, and spelling
  variants of one person are merged.
- `--report` lists every name dropped, repaired, merged or matched, with the
  reason. `docs/symposium_mentors_report.md` is the report for the current page.

- **Students' names are not published.** The page keeps each project's mentor,
  year, program, title, number of presenting students and a link to the book
  page. The script keeps the full 2007–2019 records (with names) in
  `build/symposia/legacy_records.json`, which is gitignored and stays on your
  machine. If you start from a fresh clone without that file, rebuild it from
  the v93 page in git history:
  `git show 371c904:Emory_Lab_Atlas_v93.html > build/v93.html`, then run the
  script once with `--atlas build/v93.html`. Use `--keep-students` only for
  internal checking.

To add a year: put its book in `SOURCES` at the top of the script. A new SURE
year needs nothing, because the Summer page is re-read. To re-read an
Issuu-only book properly, download its PDF from Issuu in a browser, add it to
`SOURCES` with a parser, and its old records are replaced.

# Deploying the site, and the two settings to fill in

## Settings in the page

Search the HTML for these placeholders and replace them; left as they are, the
feature stays switched off:

- `__CONTACT_EMAIL__` is the address behind the Contact link and the "Want this
  for your campus?" form. While it's unset, both are hidden.
- `__ANALYTICS_KIND__`, `__ANALYTICS_ENDPOINT__`, `__ANALYTICS_DOMAIN__` and
  `__ANALYTICS_WEBSITE__` turn on usage counts. The page counts searches,
  profile opens, email clicks, saves, outreach marks and experiences saved.
  Counts never include names, search text or cookies, and nothing is counted
  when the browser sends Do Not Track or Global Privacy Control.
  - Plausible: kind `plausible`, endpoint `https://plausible.io/api/event` (or
    your own instance), domain = the site's domain.
  - Umami: kind `umami`, endpoint `https://<your-umami>/api/send`, website = the
    site id.
  - Counting only happens on a page served over http(s), never on a file
    opened from disk.

## A fast site for phones (`scripts/build_site.py`)

```bash
node scripts/og_image.mjs og-image.png            # the link-preview image (needs playwright)
python3 scripts/build_site.py --atlas Emory_Lab_Atlas_v97.html --out site \
    --site-url https://your-domain/
```

This writes `site/`:
- `index.html` is the page without its data or code (about 430 KB), so the landing shows at once.
- `data/` and `app/` hold the records and scripts, which load next and are cached by the browser.
- `departments/` has one plain page per department, readable by search engines
  and AI assistants without JavaScript.
- `sitemap.xml`, `robots.txt` and the share image complete it.

A search typed before the data arrives runs as soon as it does. Put `site/` on
any static host with gzip or brotli turned on (GitHub Pages, Netlify,
Cloudflare Pages).

# Google Drive sync (`scripts/drive_sync.py`, `.github/workflows/drive-sync.yml`)

This keeps the shared "Emory Lab Atlas" Drive folder and the repository in step.
- **Every new version is published to the folder.** A push that adds or
  changes `Emory_Lab_Atlas_v*.html` uploads it, and the folder's
  `Lab Atlas versions.md` lists every version, newest first.
- **Versions others put in the folder are merged in.** Every 3 hours, and on
  demand from the Actions tab, any atlas HTML in the folder or its subfolders
  that the pipeline did not publish is downloaded. A collaborator's
  `v96 kt/Emory_Lab_Atlas_v96_kt.html` is one. Each one is merged into the
  current version three ways, against the earlier version it started from:
  - the page and its scripts merge line by line;
  - the records merge person by person and field by field;
  - where both sides changed the same thing, ours is kept and the clash is listed.

  The result is committed as the next version, with its report in `docs/merges/`,
  and published back to the folder.

## Publishing every version: `scripts/drive_publish.gs` (2 minutes)

The publishing half doesn't need Google Cloud. `drive_publish.gs` is a Google
Apps Script that runs in your own Google account. Every hour it reads the
repository, and if the newest `Emory_Lab_Atlas_vNN.html` (on
`claude/exciting-carson-83od2i` or `main`) isn't in the folder yet, it copies
it there. It also writes the row in `Lab Atlas versions.md`, and it uses the
same bookkeeping file as `drive_sync.py`, so the two never duplicate a
version.

1. Open <https://script.google.com>, choose **New project**, replace the
   editor's contents with `scripts/drive_publish.gs`, and save.
2. Choose `install` in the function menu, press **Run**, and allow access.
   Sign in as an account that can edit the folder.

`install` publishes the current version at once and schedules the hourly
check; `uninstall` stops it. Apps Script handles files up to 50 MB; the
atlas is about 38 MB.

## Merging versions from the folder: one-time setup (about 10 minutes)

The merging half runs in GitHub Actions and needs Drive credentials:

1. In Google Cloud Console, create a project, enable the **Google Drive API**,
   and create an **OAuth client ID** of type **Desktop app**. Note its client ID
   and secret.
2. On your own machine, run:
   ```bash
   GDRIVE_CLIENT_ID=... GDRIVE_CLIENT_SECRET=... python3 scripts/drive_sync.py auth
   ```
   Sign in with an account that can edit the folder. The command prints a
   refresh token.
3. In the GitHub repository, add four secrets under Settings → Secrets and
   variables → Actions:
   - `GDRIVE_CLIENT_ID`
   - `GDRIVE_CLIENT_SECRET`
   - `GDRIVE_REFRESH_TOKEN`
   - `GDRIVE_FOLDER_ID`: the id in the folder's URL; for "Emory Lab Atlas" it
     is `14_ZcVAechYZ-Hqbex3s2IdGag2GuU3gG`.
4. Scheduled runs use the workflow file on the default branch. Either merge this
   branch into it, or set the repository variable `ATLAS_BRANCH` to the branch
   the atlas lives on.

To try it by hand without Drive, use a plain folder:
`python3 scripts/drive_sync.py --local /tmp/fake-drive sync --repo .`

The folder also holds a data archive whose README marks one bundle (the
private search-benchmark labels) as not to be shared with implementation
agents. The pipeline only looks at `Emory_Lab_Atlas_v*.html` files and never
opens the archives.
