#!/usr/bin/env python3
"""Read Emory's GDBBS program faculty directories and mark them in the atlas.

The atlas can show, for every investigator, which GDBBS PhD programs they take
graduate students through and whether the program roster lists them as
currently accepting students. Neither of those is anywhere in the atlas's own
source data, and neither can be guessed from a lab description, so both are
read from the programs' own faculty directories by this script.

    python3 scripts/gdbbs_scrape.py --atlas Emory_Lab_Atlas_v64.html \
                                    --out   Emory_Lab_Atlas_v65.html

That writes `gdbbs` into the atlas's data block, and every badge, filter and
count in the page turns on. Nothing else in the file is touched.

Fetching, in order of preference:

  1. Agent Reach (https://github.com/Panniantong/agent-reach), if it is
     importable. Its `web` channel reads any URL through Jina Reader and hands
     back clean Markdown, which is both easier to parse than the page source
     and less likely to be refused. Install it, or point --agent-reach at a
     checkout of the repository.
  2. Playwright with --browser, for the directories that build their list in
     JavaScript. Slowest, most faithful.
  3. Plain urllib, as a fallback.

Run it from a machine that can reach biomed.emory.edu.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

BASE = "https://biomed.emory.edu"

# Each program's own faculty directory, plus the fallbacks seen in the wild.
# The first URL that yields names wins; the rest are only tried if it does not.
PROGRAMS = {
    "BCDB": ("Biochemistry, Cell and Developmental Biology", [
        f"{BASE}/PROGRAM_SITES/BCDB/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/BCDB/guides/faculty.html",
    ]),
    "BME": ("Biomedical Engineering", [
        f"{BASE}/PROGRAM_SITES/BME/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/BME/guides/faculty.html",
    ]),
    "BP": ("Biological and Biomedical Physics", [
        f"{BASE}/PROGRAM_SITES/BP/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/BP/guides/faculty.html",
    ]),
    "CB": ("Cancer Biology", [
        f"{BASE}/PROGRAM_SITES/CB/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/CB/guides/faculty.html",
    ]),
    "GMB": ("Genetics and Molecular Biology", [
        f"{BASE}/PROGRAM_SITES/GMB/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/GMB/guides/faculty.html",
    ]),
    "IMP": ("Immunology and Molecular Pathogenesis", [
        f"{BASE}/PROGRAM_SITES/IMP/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/IMP/guides/faculty.html",
    ]),
    "MMG": ("Microbiology and Molecular Genetics", [
        f"{BASE}/PROGRAM_SITES/MMG/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/MMG/guides/faculty.html",
    ]),
    "MSP": ("Molecular and Systems Pharmacology", [
        f"{BASE}/PROGRAM_SITES/MSP/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/MSP/guides/faculty.html",
    ]),
    "NS": ("Neuroscience", [
        f"{BASE}/PROGRAM_SITES/NS/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/NS/guides/faculty.html",
    ]),
    "PBEE": ("Population Biology, Ecology and Evolution", [
        f"{BASE}/PROGRAM_SITES/PBEE/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/PBEE/guides/faculty.html",
    ]),
}

# The division-wide roster. Used to catch anyone a program page missed; the
# program attribution for these rows comes from whichever program pages name
# them, so a name found only here is marked GDBBS with no program.
ALL_FACULTY = f"{BASE}/about-us/faculty-search.html"

ACCEPTING = re.compile(
    r"(accepting\s+(new\s+)?(graduate\s+|rotation\s+)?students"
    r"|currently\s+accepting"
    r"|taking\s+(new\s+)?students"
    r"|open\s+to\s+rotation)", re.I)
NOT_ACCEPTING = re.compile(
    r"(not\s+(currently\s+)?accepting|no\s+longer\s+accepting|closed\s+to\s+rotation)", re.I)

# A person's name as these directories write it: two to four capitalised words,
# middle initials with or without a full stop, optionally trailed by degrees.
_WORD = r"[A-Z][A-Za-z'\u2019\-]{1,}"
_PART = r"(?:" + _WORD + r"|[A-Z]\.?|van|von|de|del|della|da|di|la|le|dos|ter|Mc|Mac)"
_DEGREES = r"(?:Ph\.?\s?D|M\.?D|D\.?V\.?M|D\.?D\.?S|Sc\.?D|M\.?P\.?H|M\.?S|D\.?Phil|M\.?B\.?B\.?S|R\.?N|Pharm\.?D)"
NAME = re.compile(r"^(" + _WORD + r"(?:\s+" + _PART + r"){1,3})"
                  r"(?:\s*,?\s*" + _DEGREES + r"[.\w\s,/&-]*)?$")
# "Corces, Victor" and "Conn, Graeme L., PhD" are the other common shape
NAME_REV = re.compile(r"^(" + _WORD + r")\s*,\s*(" + _WORD + r"(?:\s+" + _PART + r"){0,2})"
                      r"(?:\s*,?\s*" + _DEGREES + r"[.\w\s,/&-]*)?$")

# Anything carrying one of these is a heading, a job title or a bit of site
# furniture, never a person's name on its own line.
ROLE = re.compile(
    r"\b(professor|prof|faculty|lecturer|instructor|director|chair|chairman|chairwoman|dean|"
    r"fellow|fellows|scientist|scholar|adjunct|affiliate|emeritus|emerita|associate|assistant|"
    r"program|programme|department|division|school|college|center|centre|institute|laboratory|"
    r"university|hospital|clinic|graduate|student|students|research|admissions|contact|search|"
    r"menu|home|news|events|overview|people|alumni|seminar|apply|giving|login|resources|"
    r"accepting|rotation|publications|profile|email|phone|website|more|back|next|previous)\b",
    re.I)

STOPWORDS = {
    "emory university", "graduate division", "faculty search", "our faculty",
    "program sites", "contact us", "about us", "quick links", "skip to",
    "read more", "learn more", "apply now", "student life", "privacy policy",
    "graduate school", "school of medicine", "rollins school", "laney graduate",
}


# --------------------------------------------------------------------------
# fetching
# --------------------------------------------------------------------------
def _agent_reach_reader(repo: str | None):
    """Return Agent Reach's web reader, or None if it is not available."""
    if repo:
        sys.path.insert(0, str(Path(repo).expanduser().resolve()))
    try:
        from agent_reach.channels.web import WebChannel  # type: ignore
    except Exception:
        return None
    channel = WebChannel()
    try:
        channel.check()
    except Exception:
        pass

    def read(url: str) -> str:
        return channel.read(url)

    return read


def _urllib_reader():
    import urllib.request

    def read(url: str) -> str:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; EmoryLabAtlas/1.0; +https://github.com/)",
            "Accept": "text/html,application/xhtml+xml",
        })
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")

    return read


def _browser_reader():
    from playwright.sync_api import sync_playwright  # type: ignore

    def read(url: str) -> str:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            p = b.new_page()
            p.goto(url, wait_until="networkidle", timeout=90_000)
            # the directories paginate; pull every page in before reading
            for _ in range(40):
                more = p.query_selector(
                    "button:has-text('Load more'), a:has-text('Next'), .pagination-next:not(.disabled)")
                if not more:
                    break
                try:
                    more.click(timeout=3000)
                    p.wait_for_timeout(700)
                except Exception:
                    break
            html = p.content()
            b.close()
            return html

    return read


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------
class _Text(HTMLParser):
    """HTML to newline-separated text, keeping one block per element."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        elif tag in ("br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "td", "section", "article"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = max(0, self._skip - 1)
        elif tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4", "td", "section", "article"):
            self.out.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.out.append(data)

    def text(self) -> str:
        return re.sub(r"[ \t ]+", " ", "".join(self.out))


def to_text(body: str) -> str:
    if "<" in body and ">" in body and re.search(r"<\s*(html|div|body|li|table)", body, re.I):
        p = _Text()
        p.feed(body)
        body = p.text()
    return "\n".join(line.strip() for line in body.splitlines())


def looks_like_name(line: str) -> str | None:
    line = line.strip(" \t|*-#>\u2022\u00b7")
    if not (4 <= len(line) <= 70):
        return None
    low = line.lower()
    if any(s in low for s in STOPWORDS) or ROLE.search(line):
        return None
    if any(ch.isdigit() for ch in line) or "@" in line or "http" in low:
        return None
    m = NAME_REV.match(line)
    name = f"{m.group(2)} {m.group(1)}" if m else None
    if not name:
        m = NAME.match(line)
        name = m.group(1) if m else None
    if not name:
        return None
    parts = re.sub(r"\s+", " ", name).strip().split(" ")
    # first and last have to be words rather than initials, or it is not a name
    if len(parts) < 2 or len(parts[0].rstrip(".")) < 2 or len(parts[-1].rstrip(".")) < 2:
        return None
    return " ".join(parts)


def parse_people(body: str) -> dict[str, bool | None]:
    """Names on a directory page, each with what the page says about students.

    A page that carries no accepting/not-accepting wording anywhere leaves the
    flag at None, which the atlas renders as "GDBBS faculty" with no claim
    about students either way.
    """
    text = to_text(body)
    lines = text.splitlines()
    page_says_anything = bool(ACCEPTING.search(text) or NOT_ACCEPTING.search(text))
    found: dict[str, bool | None] = {}
    for i, line in enumerate(lines):
        name = looks_like_name(line)
        if not name:
            continue
        flag: bool | None = None
        if page_says_anything:
            # the entry's own block: the few lines that belong to this card,
            # stopping at the next name so one person's badge is not read onto
            # the person below them
            block = []
            for j in range(i + 1, min(i + 9, len(lines))):
                if looks_like_name(lines[j]):
                    break
                block.append(lines[j])
            around = " ".join(block)
            if NOT_ACCEPTING.search(around):
                flag = False
            elif ACCEPTING.search(around):
                flag = True
        prev = found.get(name, "missing")
        if prev == "missing" or (prev is None and flag is not None):
            found[name] = flag
    return found


def norm_key(name: str) -> str:
    n = unicodedata.normalize("NFKD", name.lower())
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r"[^a-z]+", " ", n)
    n = re.sub(r"\b(jr|sr|ii|iii|iv|md|phd|dvm|dds|mph|msc|ms|ba|bs|dr|prof|professor)\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def variants(name: str) -> set:
    """The forms a name is matched on, on both sides of the join.

    The same three forms the page itself computes, so a name this script counts
    as matched is a name the atlas will actually mark.
    """
    raw = str(name or "")
    if "," in raw:                                   # "Corces, Victor M."
        raw = " ".join(reversed(raw.split(",")))
    w = norm_key(raw).split()
    if len(w) < 2:
        return {w[0]} if w else set()
    return {" ".join(w), w[0] + " " + w[-1], w[0][0] + " " + w[-1]}


# --------------------------------------------------------------------------
# the atlas file
# --------------------------------------------------------------------------
DATA_OPEN = '<script id="atlasdata" type="application/json">'


def patch_atlas(atlas: Path, out: Path, roster: dict) -> int:
    src = atlas.read_text(encoding="utf-8")
    i = src.index(DATA_OPEN) + len(DATA_OPEN)
    j = src.index("</script>", i)
    data = json.loads(src[i:j])
    data["gdbbs"] = roster
    out.write_text(src[:i] + json.dumps(data, separators=(",", ":")) + src[j:], encoding="utf-8")

    # How many of the roster land on a record, counted the way the page counts
    # it: a form that two roster entries share, or that two records share, is
    # struck out rather than resolved by whichever was read first.
    roster_seen, roster_amb = {}, set()
    for k in roster["people"]:
        for v in variants(k):
            if v in roster_seen and roster_seen[v] != k:
                roster_amb.add(v)
            roster_seen.setdefault(v, k)
    mine = {}
    for pi in data["pis"]:
        for v in variants(pi.get("n", "")):
            mine[v] = mine.get(v, 0) + 1
    claimed = set()
    for pi in data["pis"]:
        for v in variants(pi.get("n", "")):
            if v in roster_amb or mine.get(v, 0) > 1:
                continue
            if v in roster_seen:
                claimed.add(roster_seen[v])
                break
    return len(claimed)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--atlas", type=Path, help="the atlas HTML to read")
    ap.add_argument("--out", type=Path, help="where to write the marked copy")
    ap.add_argument("--json", type=Path, default=Path("gdbbs.json"),
                    help="where to write the roster on its own (default: gdbbs.json)")
    ap.add_argument("--agent-reach", metavar="PATH",
                    help="a checkout of the Agent Reach repository to import from")
    ap.add_argument("--browser", action="store_true",
                    help="render each directory with Playwright first (slow, most faithful)")
    ap.add_argument("--only", metavar="CODE", nargs="*",
                    help="read only these programs, e.g. --only BCDB MMG")
    ap.add_argument("--from-json", type=Path,
                    help="skip fetching and patch the atlas from a roster written earlier")
    args = ap.parse_args()

    if args.from_json:
        roster = json.loads(args.from_json.read_text(encoding="utf-8"))
    else:
        if args.browser:
            read = _browser_reader()
            how = "playwright"
        else:
            read = _agent_reach_reader(args.agent_reach)
            how = "agent-reach"
            if read is None:
                read = _urllib_reader()
                how = "urllib"
                print("Agent Reach not importable; falling back to a plain fetch.\n"
                      "  pip install agent-reach   (or  --agent-reach /path/to/Agent-Reach-main)",
                      file=sys.stderr)
        print(f"reading the GDBBS directories via {how}\n", file=sys.stderr)

        people: dict[str, dict] = {}
        codes = [c.upper() for c in (args.only or PROGRAMS)]
        for code in codes:
            if code not in PROGRAMS:
                print(f"  {code:<5} unknown program, skipped", file=sys.stderr)
                continue
            label, urls = PROGRAMS[code]
            got: dict[str, bool | None] = {}
            used = ""
            for url in urls:
                try:
                    got = parse_people(read(url))
                except Exception as e:  # a program with no page of its own
                    print(f"  {code:<5} {url} -> {type(e).__name__}: {e}", file=sys.stderr)
                    continue
                if got:
                    used = url
                    break
            print(f"  {code:<5} {len(got):>4} names  {used or 'nothing found'}", file=sys.stderr)
            for name, flag in got.items():
                rec = people.setdefault(name, {"p": [], "a": False, "u": used})
                if code not in rec["p"]:
                    rec["p"].append(code)
                if flag:
                    rec["a"] = True

        try:
            extra = parse_people(read(ALL_FACULTY))
            new = 0
            for name, flag in extra.items():
                if name not in people:
                    people[name] = {"p": [], "a": bool(flag), "u": ALL_FACULTY}
                    new += 1
                elif flag:
                    people[name]["a"] = True
            print(f"  ALL   {len(extra):>4} names  {ALL_FACULTY}  (+{new} not on a program page)",
                  file=sys.stderr)
        except Exception as e:
            print(f"  ALL   {type(e).__name__}: {e}", file=sys.stderr)

        roster = {
            "generated": _dt.date.today().isoformat(),
            "source": BASE,
            "programs": {k: v[0] for k, v in PROGRAMS.items()},
            "people": people,
        }
        args.json.write_text(json.dumps(roster, indent=1, sort_keys=True), encoding="utf-8")
        print(f"\nwrote {args.json} — {len(people)} people, "
              f"{sum(1 for v in people.values() if v['a'])} accepting students", file=sys.stderr)

    if args.atlas:
        out = args.out or args.atlas
        hit = patch_atlas(args.atlas, out, roster)
        print(f"wrote {out} — {hit} of {len(roster['people'])} roster names "
              f"matched an investigator in the atlas", file=sys.stderr)
        if hit == 0:
            print("no matches: check that the directories were parsed as names "
                  "(look in the roster JSON) before trusting the run", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
