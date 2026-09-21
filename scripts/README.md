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

## Three ways to get one

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

Load the file into the atlas: **Notes → Load a GDBBS roster → Choose a file**,
or just drop it anywhere on the page. It is kept in that browser, so it survives
a reload without anyone rewriting a forty-megabyte file.

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

`gdbbs.json` from either route works in the other — the script will apply a
collector file with `--from-json`, and the atlas will load a script file.

### 3. Paste a directory page

Nothing installed at all: open a program's faculty directory, select the whole
page, copy it, and paste it into **Notes → Load a GDBBS roster → A directory
page, pasted**, picking the program it belongs to. The names and the
accepting-students wording are read out of it in the page, by the same rules the
script uses. Ten pastes and you have the set.

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
