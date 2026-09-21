#!/usr/bin/env python3
"""Read Emory's BCDB faculty directory and write a roster the atlas can load.

    python3 bcdb_scrape.py

Standard library only - nothing to install. It fetches the BCDB faculty page,
pulls out the faculty names and whether each is listed as accepting graduate
students, prints what it found, and writes gdbbs.json.

Load that file into the atlas: Notes -> Load a GDBBS roster -> Choose a file.
Or write it straight into a copy of the atlas:

    python3 bcdb_scrape.py --atlas Emory_Lab_Atlas_v64.html --out marked.html

Other programs, once BCDB looks right:

    python3 bcdb_scrape.py --program MMG
    python3 bcdb_scrape.py --program CB --json cb.json

The raw page is always saved next to the output. If the parse comes back empty
the list is being built by JavaScript, the delivered HTML is a shell, and that
saved file is the thing to look at (or hand over) to find out what it holds.
"""

from __future__ import annotations

import argparse
import datetime
import gzip
import io
import json
import re
import sys
import unicodedata
import zlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://biomed.emory.edu"
PROGRAMS = {
    "BCDB": "Biochemistry, Cell and Developmental Biology",
    "BME": "Biomedical Engineering",
    "BP": "Biological and Biomedical Physics",
    "CB": "Cancer Biology",
    "GMB": "Genetics and Molecular Biology",
    "IMP": "Immunology and Molecular Pathogenesis",
    "MMG": "Microbiology and Molecular Genetics",
    "MSP": "Molecular and Systems Pharmacology",
    "NS": "Neuroscience",
    "PBEE": "Population Biology, Ecology and Evolution",
}


def urls_for(code: str) -> list[str]:
    return [
        f"{BASE}/PROGRAM_SITES/{code}/about-us/faculty-search.html",
        f"{BASE}/PROGRAM_SITES/{code}/guides/faculty.html",
        f"{BASE}/PROGRAM_SITES/{code}/about-us/faculty.html",
    ]


# --------------------------------------------------------------------------
# what counts as a name, and what the page says about students
# --------------------------------------------------------------------------
ACCEPT = re.compile(r"(accepting\s+(new\s+)?(graduate\s+|rotation\s+)?students"
                    r"|currently\s+accepting|taking\s+(new\s+)?students"
                    r"|open\s+to\s+rotation)", re.I)
REFUSE = re.compile(r"(not\s+(currently\s+)?accepting|no\s+longer\s+accepting"
                    r"|closed\s+to\s+rotation)", re.I)

# a heading, a job title or a bit of site furniture is never a person's name
ROLE = re.compile(
    r"\b(professor|prof|faculty|lecturer|instructor|director|chair|chairman|chairwoman|dean|"
    r"fellow|fellows|scientist|scholar|adjunct|affiliate|emeritus|emerita|associate|assistant|"
    r"program|programme|department|division|school|college|center|centre|institute|laboratory|"
    r"university|hospital|clinic|graduate|student|students|research|admissions|contact|search|"
    r"menu|home|news|events|overview|people|alumni|seminar|apply|giving|login|resources|"
    r"accepting|rotation|publications|profile|email|phone|website|more|back|next|previous)\b", re.I)

_W = r"[A-Z][A-Za-z'’\-]{1,}"
_P = (r"(?:" + _W + r"|[A-Z]\.?|van|von|der|den|ten|ter|de|del|della|da|di|dos|du|"
      r"la|le|op|bin|ibn|al|abu|st|Mc|Mac)")
_D = (r"(?:Ph\.?\s?D|M\.?D|D\.?V\.?M|D\.?D\.?S|Sc\.?D|M\.?P\.?H|M\.?S|D\.?Phil"
      r"|M\.?B\.?B\.?S|R\.?N|Pharm\.?D)")
NAME = re.compile(r"^(" + _W + r"(?:\s+" + _P + r"){1,4})(?:\s*,?\s*" + _D + r"[.\w\s,/&-]*)?$")
NAME_REV = re.compile(r"^(" + _W + r"(?:\s+" + _P + r"){0,2})\s*,\s*(" + _W + r"(?:\s+" + _P + r"){0,2})"
                      r"(?:\s*,?\s*" + _D + r"[.\w\s,/&-]*)?$")
# A unit is not a person. None of these is a plausible surname, and they turn
# up constantly in the cell or line next to a name.
FIELD = re.compile(
    r"\b(genetics|genomics|proteomics|biology|biochemistry|chemistry|medicine|pediatrics|"
    r"paediatrics|surgery|neurology|neuroscience|pathology|immunology|microbiology|"
    r"pharmacology|physiology|psychiatry|psychology|radiology|oncology|epidemiology|"
    r"biostatistics|informatics|engineering|nursing|ophthalmology|dermatology|"
    r"anesthesiology|anaesthesiology|urology|orthopaedics|orthopedics|cardiology|"
    r"physics|mathematics|statistics|sociology|anthropology|economics|ecology|evolution|"
    r"pulmonology|endocrinology|rheumatology|nephrology|hematology|haematology|"
    r"gastroenterology|obstetrics|gynecology|gynaecology|otolaryngology|radiation)\b", re.I)

JUNK = ("emory university", "graduate division", "faculty search", "our faculty", "program sites",
        "contact us", "about us", "quick links", "read more", "learn more", "apply now",
        "privacy policy")


def as_name(line: str) -> str | None:
    """A person's name, or None. Accepts 'First Last' and 'Last, First'."""
    line = str(line or "").strip(" \t|*-#>•·\n")
    if not (4 <= len(line) <= 70):
        return None
    low = line.lower()
    if any(j in low for j in JUNK) or ROLE.search(line) or FIELD.search(line):
        return None
    if any(c.isdigit() for c in line) or "@" in line or "http" in low:
        return None
    # a generational suffix is not part of the name the atlas holds, and the
    # atlas strips it on its side too, so it comes off before matching
    line = re.sub(r"[,\s]+(?:Jr|Sr|II|III|IV|V)\.?$", "", line, flags=re.I).strip()
    m = NAME.match(line)
    name = m.group(1) if m else None
    if not name:
        # "Corces, Victor" and "Aaron, Maria M., MD" - a comma the plain form
        # cannot take, so the halves are the other way round
        m = NAME_REV.match(line)
        name = f"{m.group(2)} {m.group(1)}" if m else None
    if not name:
        return None
    parts = re.sub(r"\s+", " ", name).strip().split(" ")
    # first and last have to be words rather than initials, or it is not a name
    if len(parts) < 2 or len(parts[0].rstrip(".")) < 2 or len(parts[-1].rstrip(".")) < 2:
        return None
    return " ".join(parts)


def flag_in(text: str) -> bool | None:
    if REFUSE.search(text):
        return False
    if ACCEPT.search(text):
        return True
    return None


# --------------------------------------------------------------------------
# a very small DOM, so entries can be read as cards rather than as lines
# --------------------------------------------------------------------------
VOID = {"br", "img", "input", "hr", "meta", "link", "source", "area", "base", "col", "embed"}
BLOCK = {"p", "div", "li", "tr", "td", "th", "br", "h1", "h2", "h3", "h4", "h5", "h6",
         "section", "article", "header", "footer", "nav", "ul", "ol", "dl", "dt", "dd",
         "table", "figure", "figcaption", "blockquote", "aside", "main", "form", "hr"}
CARDISH = re.compile(r"(faculty|person|people|profile|card|member|directory|teaser|result|entry|bio)", re.I)
# Site chrome. Its links are captions - "Request Info", "Privacy Statement" -
# and two capitalised words in a menu look exactly like a name to a regex, so
# the whole subtree comes out before anything is read.
NAVISH = re.compile(r"(^|[\s_-])(nav|menu|breadcrumb|sidebar|side-bar|utility|skip|banner|"
                    r"masthead|footer|header|subnav|megamenu|toolbar|social|share|cookie|"
                    r"drawer|offcanvas|search-form|pagination)([\s_-]|$)", re.I)
NAV_TAGS = {"nav", "header", "footer", "aside"}
# a class that says "this element is the person's name"
NAMEISH = re.compile(r"(^|[\s_-])(name|fullname|full-name|title|heading)([\s_-]|$)", re.I)


class Node:
    __slots__ = ("tag", "attrs", "kids", "parent")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.kids, self.parent = tag, attrs or {}, [], parent

    def text(self) -> str:
        out = []

        def walk(n):
            for k in n.kids:
                if isinstance(k, str):
                    out.append(k)
                elif k.tag in ("script", "style", "noscript"):
                    continue
                else:
                    if k.tag in BLOCK:
                        out.append("\n")
                    walk(k)
                    if k.tag in BLOCK:
                        out.append("\n")
        walk(self)
        return re.sub(r"[ \t ]+", " ", "".join(out))

    def find(self, tags):
        for k in self.kids:
            if isinstance(k, str):
                continue
            if k.tag in tags:
                yield k
            yield from k.find(tags)


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root
        self.scripts: list[str] = []
        self._in_script = False

    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs), self.cur)
        self.cur.kids.append(n)
        if tag == "script":
            self._in_script = True
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, dict(attrs), self.cur))

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        if self._in_script:
            self.scripts.append(data)
        else:
            self.cur.kids.append(data)


# --------------------------------------------------------------------------
# the three ways a name can be found on one of these pages
# --------------------------------------------------------------------------
def strip_chrome(tree: Tree) -> int:
    """Drop navigation, headers, footers and menus. Returns how many went."""
    gone = 0

    def walk(node):
        nonlocal gone
        keep = []
        for k in node.kids:
            if isinstance(k, str):
                keep.append(k)
                continue
            cls = " ".join([k.attrs.get("class", ""), k.attrs.get("id", ""),
                            k.attrs.get("role", "")])
            if k.tag in NAV_TAGS or NAVISH.search(cls):
                gone += 1
                continue
            walk(k)
            keep.append(k)
        node.kids = keep

    walk(tree.root)
    return gone


def scan_cards(tree: Tree) -> dict[str, bool | None]:
    """Elements that look like a faculty card: heading inside gives the name,
    the card's own text says whether they are taking students."""
    found: dict[str, bool | None] = {}
    cards = []
    for node in tree.root.find({"div", "li", "article", "section", "tr"}):
        cls = " ".join([node.attrs.get("class", ""), node.attrs.get("id", "")])
        if CARDISH.search(cls):
            cards.append(node)
    # Only the innermost ones. A list is usually called faculty-something too,
    # and reading the whole list as a single card takes the first person's name
    # and the first students wording anywhere under it - which is how one
    # person's "not accepting" ends up on somebody else.
    inner = []
    for node in cards:
        if any(k is not node for k in node.find({"div", "li", "article", "section", "tr"})
               if k in cards):
            continue
        inner.append(node)
    for node in inner:
        body = node.text()
        if len(body) > 1200:                       # still a container, not a card
            continue
        name = None
        # the name as the card marks it: a heading or link first, then an
        # element whose class says it is the name
        for h in node.find({"h1", "h2", "h3", "h4", "h5", "h6", "a", "strong", "b"}):
            name = as_name(h.text().strip())
            if name:
                break
        if not name:
            for h in node.find({"span", "div", "p", "td"}):
                cls = " ".join([h.attrs.get("class", ""), h.attrs.get("id", "")])
                if NAMEISH.search(cls):
                    name = as_name(h.text().strip())
                    if name:
                        break
        if not name:
            continue
        f = flag_in(body)
        if name not in found or (found[name] is None and f is not None):
            found[name] = f
    return found


def linked_names(tree: Tree) -> set:
    """Names as the page itself marks them up - in a link or a heading.

    On a page that does this, a run of capitalised words sitting in some other
    cell is a department, a building or a research area, not a person. So the
    line scan is held to this set wherever the page provides one.
    """
    out = set()
    for n in tree.root.find({"a", "h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"}):
        name = as_name(n.text().strip())
        if name:
            out.add(name)
    # plenty of directories put the name in a span or div with a telling class
    for n in tree.root.find({"span", "div", "p", "td"}):
        cls = " ".join([n.attrs.get("class", ""), n.attrs.get("id", "")])
        if not NAMEISH.search(cls):
            continue
        name = as_name(n.text().strip())
        if name:
            out.add(name)
    return out


def scan_lines(tree: Tree, allowed: set | None = None) -> dict[str, bool | None]:
    """Whole-page text, one line per block: a name, then the few lines under it."""
    lines = [ln.strip() for ln in tree.root.text().splitlines()]
    says = any(ACCEPT.search(ln) or REFUSE.search(ln) for ln in lines)
    found: dict[str, bool | None] = {}
    for i, ln in enumerate(lines):
        name = as_name(ln)
        if not name or (allowed and name not in allowed):
            continue
        f = None
        if says:
            block = []
            for j in range(i + 1, min(i + 9, len(lines))):
                nxt = as_name(lines[j])
                if nxt and (not allowed or nxt in allowed):
                    break                          # the next person's card
                block.append(lines[j])
            f = flag_in(" ".join(block))
        if name not in found or (found[name] is None and f is not None):
            found[name] = f
    return found


def scan_scripts(tree: Tree) -> dict[str, bool | None]:
    """A directory that renders from an embedded payload keeps its names in a
    <script>. No students flag is attributed from these - it cannot be tied to
    a person reliably - so they come back unknown."""
    found: dict[str, bool | None] = {}
    for src in tree.scripts:
        if len(src) < 40 or not re.search(r"name|faculty", src, re.I):
            continue
        for hit in re.findall(r'"(?:name|fullName|full_name|displayName|title)"\s*:\s*"([^"]{4,70})"', src):
            n = as_name(hit)
            if n:
                found.setdefault(n, None)
    return found


# --------------------------------------------------------------------------
def diagnose(html: str, tree: Tree) -> None:
    """When nothing is found, say what the page actually holds.

    A directory that renders its list client-side still has to say where the
    list comes from. That is usually a URL in a script, or a payload keyed by
    something obvious, and it is nearly always visible in the delivered HTML.
    """
    print("  what the page does contain:")

    # the classes that repeat: the shape of a list, if there is one
    classes: dict[str, int] = {}
    for n in tree.root.find({"div", "li", "article", "section", "tr", "span"}):
        for c in (n.attrs.get("class", "") or "").split():
            if len(c) > 2:
                classes[c] = classes.get(c, 0) + 1
    top = sorted(classes.items(), key=lambda kv: -kv[1])[:8]
    if top:
        print("    repeated classes : " + ", ".join(f"{c}x{n}" for c, n in top))

    # anything that looks like it serves data
    urls = set()
    for m in re.finditer(r"""['"](/[^'"\s]{4,120}|https?://[^'"\s]{6,160})['"]""", html):
        u = m.group(1)
        if re.search(r"(\.json|/api/|/ajax|/rest/|/services/|/feed|/search\?|/query|graphql|"
                     r"faculty.*\.(js|json)|solr|elastic)", u, re.I):
            urls.add(u)
    if urls:
        print("    data-ish URLs    :")
        for u in sorted(urls)[:10]:
            print(f"       {u if u.startswith('http') else BASE + u}")
    else:
        print("    data-ish URLs    : none found")

    # scripts are where a client-rendered list usually hides
    big = sorted((len(x) for x in tree.scripts), reverse=True)[:3]
    if big:
        print(f"    inline scripts   : {len(tree.scripts)}, largest {big[0]:,} chars")
    srcs = [n.attrs.get("src", "") for n in tree.root.find({"script"}) if n.attrs.get("src")]
    app = [u for u in srcs if re.search(r"(app|main|bundle|faculty|directory|search)", u, re.I)]
    if app:
        print("    app scripts      : " + ", ".join(app[:4]))
    print()


def fetch(url: str, timeout: int = 45) -> str:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urlopen(req, timeout=timeout) as r:
        raw = r.read()
        enc = (r.headers.get("Content-Encoding") or "").lower()
        if enc == "gzip":
            raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
        elif enc == "deflate":
            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
        charset = r.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, "replace")


def norm(name: str) -> str:
    n = unicodedata.normalize("NFKD", name.lower())
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r"[^a-z]+", " ", n)
    n = re.sub(r"\b(jr|sr|ii|iii|iv|md|phd|dvm|dds|mph|msc|ms|ba|bs|dr|prof|professor)\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def variants(name: str) -> set:
    raw = str(name or "")
    if "," in raw:
        raw = " ".join(reversed(raw.split(",")))
    w = norm(raw).split()
    if len(w) < 2:
        return {w[0]} if w else set()
    return {" ".join(w), w[0] + " " + w[-1], w[0][0] + " " + w[-1]}


def patch_atlas(atlas: Path, out: Path, roster: dict) -> int:
    OPEN = '<script id="atlasdata" type="application/json">'
    src = atlas.read_text(encoding="utf-8")
    i = src.index(OPEN) + len(OPEN)
    j = src.index("</script>", i)
    data = json.loads(src[i:j])
    data.setdefault("gdbbs", {"generated": roster["generated"], "source": roster["source"],
                              "programs": roster["programs"], "people": {}})
    data["gdbbs"]["people"].update(roster["people"])
    data["gdbbs"]["generated"] = roster["generated"]
    out.write_text(src[:i] + json.dumps(data, separators=(",", ":")) + src[j:], encoding="utf-8")

    # counted the way the page counts it: a form two people share is struck out
    seen, amb = {}, set()
    for k in data["gdbbs"]["people"]:
        for v in variants(k):
            if v in seen and seen[v] != k:
                amb.add(v)
            seen.setdefault(v, k)
    mine = {}
    for pi in data["pis"]:
        for v in variants(pi.get("n", "")):
            mine[v] = mine.get(v, 0) + 1
    claimed = set()
    for pi in data["pis"]:
        for v in variants(pi.get("n", "")):
            if v in amb or mine.get(v, 0) > 1:
                continue
            if v in seen:
                claimed.add(seen[v])
                break
    return len(claimed)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--program", default="BCDB", help="program code (default BCDB)")
    ap.add_argument("--url", help="read this URL instead of the program's usual pages")
    ap.add_argument("--json", type=Path, default=Path("gdbbs.json"), help="roster output")
    ap.add_argument("--raw", type=Path, help="where to save the page as delivered")
    ap.add_argument("--atlas", type=Path, help="an atlas HTML to write the roster into")
    ap.add_argument("--out", type=Path, help="where to write the marked atlas")
    ap.add_argument("--quiet", action="store_true", help="skip the name-by-name listing")
    a = ap.parse_args()

    code = a.program.upper()
    label = PROGRAMS.get(code, code)
    raw_path = a.raw or Path(f"{code.lower()}_page.html")
    tried = [a.url] if a.url else urls_for(code)

    print(f"\nEmory {code} faculty directory  -  {label}\n")
    html = used = None
    for url in tried:
        print(f"  fetching {url}")
        try:
            html = fetch(url)
        except Exception as e:
            print(f"      {type(e).__name__}: {e}")
            continue
        used = url
        break
    if html is None:
        print("\n  Could not fetch any of the pages above.")
        print("  If this machine is behind a proxy or off the network, use the browser")
        print("  route instead: scripts/collect_gdbbs.js\n")
        return 1

    raw_path.write_text(html, encoding="utf-8")
    print(f"      {len(html):,} characters, saved to {raw_path}\n")

    tree = Tree()
    tree.feed(html)
    dropped = strip_chrome(tree)
    linked = linked_names(tree)
    by_card = scan_cards(tree)
    # Held to the marked-up names only where there are enough of them to be a
    # roster. Two or three is a caption, and letting those govern the line scan
    # is how a page of navigation turns into a page of "faculty".
    by_line = scan_lines(tree, linked if len(linked) >= 3 else None)
    by_script = scan_scripts(tree)
    print(f"  cards          {len(by_card):>4} names")
    print(f"  page text      {len(by_line):>4} names")
    print(f"  embedded JSON  {len(by_script):>4} names")
    if dropped:
        print(f"  ({dropped} navigation, header and footer blocks set aside first)")
    if len(linked) >= 3:
        print(f"  (held to the {len(linked)} names the page marks up as its own)")

    merged: dict[str, bool | None] = {}
    for src in (by_card, by_line, by_script):          # cards are the most precise
        for n, f in src.items():
            if n not in merged or (merged[n] is None and f is not None):
                merged[n] = f

    if not merged:
        print("\n  !! No names found.\n")
        diagnose(html, tree)
        print("  The delivered HTML holds no list, which almost always means the page")
        print("  builds it in JavaScript after loading. Two ways on from here:")
        print(f"    - look in {raw_path} to see what it actually contains")
        print("    - use the browser route, which renders the page first:")
        print("      scripts/collect_gdbbs.js, then  await GDBBS.all()\n")
        return 2

    yes = sum(1 for f in merged.values() if f is True)
    no = sum(1 for f in merged.values() if f is False)
    print(f"\n  {len(merged)} people  -  {yes} accepting students, {no} not, "
          f"{len(merged) - yes - no} not stated\n")
    if not a.quiet:
        for n in sorted(merged, key=lambda x: x.split()[-1]):
            mark = {True: "accepting", False: "not accepting"}.get(merged[n], "-")
            print(f"    {n:<34} {mark}")
        print()

    roster = {
        "generated": datetime.date.today().isoformat(),
        "source": used,
        "programs": {code: label},
        "people": {n: {"p": [code], "a": bool(f), "u": used} for n, f in merged.items()},
    }
    a.json.write_text(json.dumps(roster, indent=1, sort_keys=True), encoding="utf-8")
    print(f"  wrote {a.json}")

    if a.atlas:
        out = a.out or a.atlas
        hit = patch_atlas(a.atlas, out, roster)
        print(f"  wrote {out}  -  {hit} of {len(merged)} tied to an investigator in the atlas")
    else:
        print("  Load it in the atlas:  Notes -> Load a GDBBS roster -> Choose a file")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
