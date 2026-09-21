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

## Running it

```bash
# 1. give the script a way to read the web (optional but preferred)
pip install agent-reach          # or: --agent-reach /path/to/Agent-Reach-main

# 2. read the directories and write the marked copy
python3 scripts/gdbbs_scrape.py \
    --atlas Emory_Lab_Atlas_v64.html \
    --out   Emory_Lab_Atlas_v65.html
```

It prints, per program, how many names it found and which URL they came from,
then how many of those names it could tie to a record in the atlas. Open
`gdbbs.json` and read a few entries before trusting a run: if a program's count
is 0, or the names look like headings rather than people, the directory's markup
has moved and the parser needs a look.

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
