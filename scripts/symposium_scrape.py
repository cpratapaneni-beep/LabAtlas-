#!/usr/bin/env python3
"""Rebuild the atlas's "Past undergrad mentors" data from Emory's
undergraduate research symposium books.

Which faculty have taken undergraduates, when, and on what project, comes from
the abstract books of the SURE (summer) and URP / SIRE (spring and fall)
symposia. Each book names the presenting student, the project and the faculty
mentor. This script reads them and writes the `surehist` block the page uses.

Sources
  * Books Emory hosts itself (fetched with --fetch, cached in --cache):
      Summer 2021 abstract book (PDF), Spring 2026 abstracts (PDF),
      the Summer symposium page (an HTML table; it carries the current year).
    These are parsed from the documents directly.
  * Books that exist only on Issuu (2007-2019). Issuu does not serve them to
    scripts, so they are read from the records already in the page (--atlas),
    which came from an earlier extraction of their text layer. That text layer
    is poor for the oldest programs (2007-2013 lost every space, so words and
    names run together), and the earlier extraction kept whatever stood in the
    mentor slot. Here every such name is checked before it is kept:
      - department, facility and sentence fragments are dropped
        ("Bioinformatics Core", "Computer Science", "We Hypothesize That ...");
      - names run into other text are recovered when they split cleanly into a
        known first name and surname ("Religion Diannestewart" -> Dianne Stewart);
      - where a project lists several people and some are known faculty (an
        atlas investigator, or a faculty mentor in a book that says so), the
        others are co-authors (graduate students, postdocs), not mentors;
      - names that are themselves presenting students are dropped.
    To re-read an Issuu book properly, download its PDF from Issuu in a browser
    and add it to SOURCES with a parser; it then replaces the old records.
  * Emory News stories are not project records and are not used.

Mentors are matched to atlas investigators by name: exact, then ignoring
middle names and initials, then a nickname table, then one-letter spelling
slips; a match is taken only when it is unique.

Usage
  python scripts/symposium_scrape.py --atlas Emory_Lab_Atlas_v99.html \
      --cache build/symposia --fetch --out build/surehist.json \
      --report build/symposium_report.md
  # then splice build/surehist.json into the page's <script id="surehist">
  # (or pass --write-atlas to do it in place)

Needs: python 3.9+, pdftotext (poppler-utils) for the PDFs.
"""
import argparse, collections, html, json, os, re, subprocess, sys, unicodedata, urllib.request

ISSUU = 'https://issuu.com/emoryundergraduateresearchprograms/docs/'
UR = 'https://college.emory.edu/undergraduate-research/'

# Books parsed from the documents. `replaces` names the old record sources the
# fresh parse supersedes.
SOURCES = [
    dict(key='sure_2021', file='sure_2021.pdf', kind='pdf2021', y=2021, term='summer', program='SURE',
         url=UR + 'documents/Symposia/Summer%202021%20Abstract%20Booklet.pdf',
         label='Summer 2021 abstract book', replaces=['sure_2021_abstract_booklet.pdf']),
    dict(key='spring_2026', file='spring_2026.pdf', kind='pdf2026', y=2026, term='spring', program='URP',
         url=UR + '_documents/Symposia/spring-2026-symposium-abstracts.pdf',
         label='Spring 2026 abstracts', replaces=['spring_2026_symposium_abstracts.pdf']),
    dict(key='summer_page', file='summer-symp.html', kind='table', y=None, term='summer', program='SURE',
         url=UR + 'summer-programs/summer-symp.html',
         label='Summer {y} symposium programme', replaces=['sure_{y}_symposium.html']),
]
# Readable names for the books only Issuu holds, by the key the old records use.
LEGACY = {
    'researchsymposiumprogramspr2007': 'Spring 2007 research symposium programme',
    'researchsymposiumfall2008': 'Fall 2008 research symposium programme',
    'researchsymposiumprogramspr2009': 'Spring 2009 research symposium programme',
    'researchsymposiumprogramfall2009': 'Fall 2009 research symposium programme',
    '2010spring': 'Spring 2010 research symposium programme',
    'webbrochurefall2011': 'Fall 2011 symposium brochure',
    'spring2012symposiumwebprogram': 'Spring 2012 symposium programme',
    'symposiumwebbrochurefall2012': 'Fall 2012 symposium brochure',
    'sire_spring_symposium_2013': 'Spring 2013 SIRE symposium',
    'sure_2016_symposium_abstract_bookle': 'Summer 2016 abstract book',
    'summer_17_science_abstract_booklet_': 'Summer 2017 science abstract book',
    'summer_18_abstract_booklet_publisha': 'Summer 2018 abstract book',
    'urp_spring_2019_symposium_abstract_': 'Spring 2019 abstract book',
    'sure_2019_symposium_abstract_bookle': 'Summer 2019 abstract book',
}

# Words that never occur in a person's name but do occur in the department,
# facility and sentence fragments the old text layer put in the mentor slot.
STOP = set('''
and the of for in on at to with by from we that this these those our their its is are was were be been
pm am mm nm um core lab labs laboratory center centre department dept school college university institute
program programme science sciences scientific computer computing biology biological chemistry physics
psychology psychiatry religion neuroscience neurosciences biochemistry bioinformatics informatics facility
studies study international oral presentation presentations poster posters hypothesize hypothesized certain
urinary syste system systems disease diseases neurological yerkes national primate research faculty mentor
mentors professor emory medicine medical health public nursing pharmacology genetics anthropology history
economics sociology philosophy literature mathematics math statistics engineering behavioral
behavioural biomedical molecular cellular cell clinical surgery pediatrics graduate undergraduate student
students abstract abstracts session room alumni small however while whereas results result method methods
data analysis effect effects role using via between during treatment group groups response responses
'''.split())
BAD_ENDINGS = ('tion', 'tions', 'ology', 'ment', 'ments', 'ness', 'ism', 'ings', 'studies', 'room', 'ance',
               'ence', 'ities', 'ysis', 'ical', 'ative', 'ously')
# places and institutions that read like a person's name
NOT_PEOPLE = {'agnes scott', 'san jose', 'california state', 'nell hodgson', 'hodgson woodruff', 'georgia tech',
              'morehouse school', 'spelman college'}
SUFFIX = {'jr', 'sr', 'ii', 'iii', 'iv', 'md', 'phd', 'dr', 'mph', 'msc', 'ms', 'rn', 'dvm', 'facs'}
NICK = {
    'sam': ['samuel'], 'will': ['william'], 'bill': ['william'], 'mike': ['michael'], 'bob': ['robert'],
    'rob': ['robert'], 'jim': ['james'], 'tom': ['thomas'], 'dave': ['david'], 'dan': ['daniel'],
    'chris': ['christopher', 'christine', 'christina'], 'kate': ['katherine', 'kathryn'], 'liz': ['elizabeth'],
    'beth': ['elizabeth'], 'nick': ['nicholas'], 'matt': ['matthew'], 'steve': ['steven', 'stephen'],
    'tony': ['anthony'], 'andy': ['andrew'], 'simba': ['simbarashe'], 'greg': ['gregory'], 'ken': ['kenneth'],
    'joe': ['joseph'], 'jeff': ['jeffrey'], 'ben': ['benjamin'], 'alex': ['alexander', 'alexandra'],
    'pat': ['patricia', 'patrick'], 'buz': ['hyder'], 'jen': ['jennifer'], 'jenny': ['jennifer'],
    'katie': ['katherine', 'kathryn'], 'rick': ['richard'], 'rich': ['richard'], 'ed': ['edward', 'edmund'],
    'don': ['donald'], 'ron': ['ronald'], 'larry': ['lawrence'], 'sue': ['susan'], 'vicki': ['victoria'],
    'nate': ['nathan', 'nathaniel'], 'zach': ['zachary'], 'jon': ['jonathan'], 'tim': ['timothy'],
    'jaap': ['jacobus'], 'tania': ['tatiana'], 'marge': ['marjorie'],
}


# ---------------------------------------------------------------- names
def fold(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))

def tokens(name):
    """Lower-case name tokens, without initials, titles or degree suffixes."""
    s = fold(name).lower().replace('.', ' ').replace(',', ' ')
    s = re.sub(r'\(.*?\)', ' ', s)
    out = [t for t in re.split(r'\s+', s) if t and t not in SUFFIX]
    if len(out) > 2:  # middle initials go, first and last stay whatever they are
        out = [out[0]] + [t for t in out[1:-1] if len(t) > 1] + [out[-1]]
    return out

def key(name):
    t = tokens(name)
    return (t[0] + ' ' + t[-1]) if len(t) >= 2 else ''

def lev1(a, b):
    """True when a and b differ by at most one edit."""
    if a == b: return True
    if abs(len(a) - len(b)) > 1: return False
    if len(a) == len(b): return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b): a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]: i += 1
    return a[i:] == b[i + 1:]

def same_first(a, b):
    """Two first names that can be one person's: equal, a one-letter slip, one
    the start of the other (Tharanga / Tharangamala), or a nickname."""
    return a == b or (min(len(a), len(b)) >= 5 and lev1(a, b)) or \
        (min(len(a), len(b)) >= 4 and (a.startswith(b) or b.startswith(a))) or \
        b in NICK.get(a, []) or a in NICK.get(b, [])

def same_person(x, y):
    tx, ty = tokens(x), tokens(y)
    return len(tx) >= 2 and len(ty) >= 2 and tx[-1] == ty[-1] and same_first(tx[0], ty[0])

def smart_case(s):
    """MCDERMOTT -> McDermott, O'CONNELL -> O'Connell, leaving mixed case alone."""
    if s != s.upper() and s != s.lower():
        return ' '.join(re.sub(r"^Mc([a-z])", lambda m: 'Mc' + m.group(1).upper(), w[:1].upper() + w[1:]) for w in s.split())
    def one(w):
        w = w.lower()
        w = '-'.join(p[:1].upper() + p[1:] for p in w.split('-'))
        w = re.sub(r"^(Mc|O')([a-z])", lambda m: m.group(1) + m.group(2).upper(), w)
        return w
    return ' '.join(one(w) for w in s.split())

def tidy(s):
    s = html.unescape(s or '').replace('​', '').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip(' ;,.')


class Names:
    """The atlas's investigators plus every name the books themselves give,
    used to match mentors and to tell a name from a fragment."""

    def __init__(self, pis, vocab=()):
        self.pis = pis
        self.vocab = {fold(w).lower() for w in vocab if isinstance(w, str)}
        self.by_key = collections.defaultdict(list)
        self.by_last = collections.defaultdict(list)
        self.first, self.last = set(), set()
        for p in pis:
            t = tokens(p['n'])
            if len(t) < 2: continue
            self.by_key[t[0] + ' ' + t[-1]].append(p['id'])
            for part in t[-1].split('-'):
                self.by_last[part].append(p['id'])
                self.last.add(part)
            self.first.add(t[0])
        self.first.update(NICK)
        self.faculty = set()   # keys of people a book calls faculty mentor
        self.students = set()  # keys of presenting students

    def learn(self, name, faculty=False, student=False):
        t = tokens(name)
        if len(t) < 2: return
        self.first.add(t[0]); self.last.update(t[-1].split('-'))
        if faculty: self.faculty.add(t[0] + ' ' + t[-1])
        if student: self.students.add(t[0] + ' ' + t[-1])

    def match(self, name):
        """(pi_id, how) or (None, None). Only unique matches count."""
        t = tokens(name)
        if len(t) < 2: return None, None
        f, l = t[0], t[-1]
        ids = self.by_key.get(f + ' ' + l, [])
        if len(ids) == 1: return ids[0], 'exact'
        if len(ids) > 1: return None, 'ambiguous'
        for alt in NICK.get(f, []):
            ids = self.by_key.get(alt + ' ' + l, [])
            if len(ids) == 1: return ids[0], 'nickname'
        # one-letter slips in the surname (len >= 6) or the first name (len >= 5)
        cands = set()
        for k, v in self.by_key.items():
            kf, kl = k.split(' ', 1)
            if kf == f and len(l) >= 6 and lev1(kl, l): cands.update(v)
            elif kl == l and len(f) >= 5 and lev1(kf, f): cands.update(v)
        if len(cands) == 1: return cands.pop(), 'spelling'
        # a longer or shorter form of the first name (Shrutiben / Shruti)
        cands = {i for k, v in self.by_key.items() if k.split(' ', 1)[1] == l and len(f) >= 4
                 and len(k.split(' ', 1)[0]) >= 4 and same_first(f, k.split(' ', 1)[0]) for i in v}
        if len(cands) == 1: return cands.pop(), 'longer or shorter first name'
        # a hyphenated surname given in part
        if '-' not in l:
            ids = [i for i in self.by_last.get(l, []) if tokens(self.pis[i]['n'])[0] == f and '-' in tokens(self.pis[i]['n'])[-1]]
            if len(ids) == 1: return ids[0], 'hyphen'
        return None, None

    def wordy(self, tok):
        """An ordinary word rather than a name: in the atlas's title vocabulary
        and not anyone's first or last name, or (when long) two such words run
        together."""
        t = fold(tok).lower().strip(".,'")
        if '-' in t: return any(self.wordy(x) for x in t.split('-') if x)
        if t in self.first or t in self.last: return False
        if t in self.vocab or t in STOP: return True
        if len(t) >= 10 and any(len(w) >= 5 and (t.startswith(w) or t.endswith(w)) for w in STOP): return True
        if len(t) >= 12:
            for i in range(3, len(t) - 2):
                if t[:i] in self.vocab and t[i:] in self.vocab: return True
        return False

    def cut_off(self, surname):
        """A short unknown surname that is the start of a longer word ('Chil', 'Ro'):
        the text layer cut the line, and this is not a name."""
        t = fold(surname).lower()
        if t in self.last or len(t) > 4: return False
        if len(t) <= 2: return True
        if not hasattr(self, '_pre'):
            self._pre = {w[:k] for w in self.vocab if len(w) >= 6 for k in range(2, 5)}
        return t in self._pre and not any(w == t for w in self.vocab)

    def known(self, name):
        k = key(name)
        if not k: return False
        if k in self.faculty or self.match(name)[0] is not None: return True
        f, l = k.split(' ', 1)
        return any(fk.endswith(' ' + l) and same_first(f, fk.split(' ', 1)[0]) for fk in self.faculty)

    def split_run(self, tok):
        """'diannestewart' -> 'Dianne Stewart', or None. Prefers splits whose
        surname is known; an unknown surname needs a first name of 4+ letters."""
        tok = fold(tok).lower()
        if not tok.isalpha() or len(tok) < 7: return None
        best = None
        for i in range(3, len(tok) - 2):
            f, rest = tok[:i], tok[i:]
            if f not in self.first: continue
            for mid, l in ((None, rest), (rest[0], rest[1:])):
                if len(l) < 3: continue
                score = 2 if l in self.last else (1 if (mid is None and len(f) >= 4 and 4 <= len(l) <= 12
                                                        and not l.endswith(BAD_ENDINGS)) else 0)
                if score and (best is None or score > best[0] or (score == best[0] and len(f) > len(best[1]))):
                    best = (score, f, mid, l)
        if not best: return None
        _, f, mid, l = best
        return ' '.join(x for x in (f.title(), (mid.upper() + '.') if mid else None, l.title()) if x)


def clean_names(raw, names, strict=False):
    """Every person in one mentor slot: [(display name, note)] or [(None, why)]."""
    s = tidy(raw)
    toks = s.split()
    low = [fold(t).lower() for t in toks]
    if len(toks) == 4 and low[:2] == low[2:]:  # "Michael Tebere Michael Tebere"
        return [clean_name(' '.join(toks[:2]), names, strict)]
    if len(toks) == 4 and low[0] in names.first and low[2] in names.first and not names.known(s) \
            and low[1] not in names.first and not names.known(' '.join(toks[1:])):
        got = [clean_name(' '.join(toks[:2]), names, strict), clean_name(' '.join(toks[2:]), names, strict)]
        return [(n, 'two names in one slot') if n else (n, w) for n, w in got]
    return [clean_name(s, names, strict)]


def clean_name(raw, names, strict=False):
    """(display name, note) for something found in a mentor slot, or (None, why).
    strict (the old records): a name nobody else confirms is dropped when it holds
    an ordinary word and no recognised first name, ends in a cut-off surname
    ('Chil'), or runs to three or more parts without a recognised first name."""
    s = tidy(raw)
    s = re.sub(r'^(dr\.?|prof\.?|professor)\s+', '', s, flags=re.I)
    s = re.sub(r'^(professor|facultymentor)(?=[a-z])', '', s, flags=re.I)  # "Professoranna Leo"
    s = tidy(re.sub(r'\b(ph\.?\s?d|m\.?d|mph|dr)\b\.?', ' ', s, flags=re.I))
    if not s: return None, 'empty'
    if names.known(s): return smart_case(s), None
    toks = s.split()
    low = [fold(t).lower().strip('.,') for t in toks]
    if key(s) in NOT_PEOPLE or ' '.join(low) in NOT_PEOPLE or any(' '.join(low[i:i + 2]) in NOT_PEOPLE for i in range(len(low) - 1)):
        return None, 'a place or institution'
    # a known name with something else after or before it ("Kyle Biegasiewicz Abigail Halloran")
    for i, j in ((0, 2), (0, 3), (len(toks) - 2, len(toks))):
        if len(toks) > 2 and 0 <= i and j <= len(toks) and j - i < len(toks) and names.known(' '.join(toks[i:j])):
            return smart_case(' '.join(toks[i:j])), 'known name cut from longer text'
    # a name with a word run onto it ("Asianstudies Joachimkurtz"), when the split finds a known surname
    for t in toks:
        tl = fold(t).lower()
        if len(t) >= 11 and t.isalpha() and tl not in names.first and tl not in names.last:
            got = names.split_run(t)
            if got and tokens(got)[-1] in names.last and (len(toks) == 1 or any(names.wordy(x) for x in toks if x != t)):
                return got, 'recovered from run-together text'
    # a first name trailing a full name ("Nicholas Cuccia Justin")
    if len(toks) == 3 and low[2] in names.first and low[2] not in names.last and low[0] in names.first:
        toks, low = toks[:2], low[:2]
        s = ' '.join(toks)
    shaped = all(re.fullmatch(r"[A-Za-z\u00C0-\u024F][A-Za-z\u00C0-\u024F'\-]*\.?", t) for t in toks)
    full = [t for t in low if len(t.strip('.')) > 1]
    if shaped and 2 <= len(toks) <= 4 and all(len(t) <= 16 for t in toks) and len(full) >= 2 and not any(t in STOP for t in low):
        # words that are not anyone's name; a recognised first or last name lets one short one through
        W = [t for t in full if names.wordy(t)]
        named = full[0] in names.first or full[-1].split('-')[-1] in names.last
        surname = full[-1].split('-')[-1] if full else ''
        if strict and ((W and full[0] not in names.first) or names.cut_off(surname) or (len(full) >= 3 and full[0] not in names.first)):
            return None, 'unconfirmed name with a word or a cut-off surname in it'
        if not W or (named and len(full) == 2 and len(W) == 1 and len(W[0]) <= 10):
            return smart_case(s), None
    # a name run into other text: try the last token, then the first
    if any(len(t) >= 11 for t in toks) or any(t in STOP for t in low):
        for t in ([toks[-1], toks[0]] if len(toks) > 1 else toks):
            tl = fold(t).lower()
            if len(t) >= 9 and t.isalpha() and tl not in names.first and tl not in names.last:
                got = names.split_run(t)
                if got: return got, 'recovered from run-together text'
    if len(toks) < 2: return None, 'single word'
    if any(len(t) > 16 for t in toks): return None, 'run-together text with no recoverable name'
    return None, 'department, facility or sentence fragment'


def split_people(s):
    s = tidy(s)
    parts = re.split(r'\s*(?:;|&|\band\b|,(?=\s*\S+\s+\S+))\s*', s, flags=re.I)
    return [p for p in (tidy(x) for x in parts) if p]


# ---------------------------------------------------------------- parsers
def pdftext(path, layout=False):
    args = ['pdftotext'] + (['-layout'] if layout else []) + [path, '-']
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout

def parse_2021(path, src):
    """Blocks: title lines, an author line ('Last, First; ...'), 'Presenter/s:',
    'Emory Faculty Mentor:'. Mostly one block a page."""
    out = []
    for pno, page in enumerate(pdftext(path).split('\f'), 1):
        lines = [l.strip() for l in page.split('\n')]
        start = 0
        for i, l in enumerate(lines):
            if l.startswith('Presentation Link:') or l.startswith('Presentation Time:'):
                start = i + 1
            if not l.startswith('Presenter/s:'): continue
            mentor = next((x.split(':', 1)[1] for x in lines[i + 1:i + 4] if re.match(r'(Emory )?Faculty Mentors?:', x)), '')
            head = [x for x in lines[start:i] if x]
            # the author list ('Last, First; Last, First ...', which may wrap) follows the title
            pres = tidy(l.split(':', 1)[1]).lower()
            def authorish(k):
                x = head[k]
                if re.match(r"^(Author \d+\s+)?[^\s,;][^,;]{0,40},\s*\S", x) and (';' in ' '.join(head[k:]) or k == len(head) - 1):
                    return True          # Last, First; Last, First
                segs = [g.strip() for g in x.split(';') if g.strip()]
                if len(segs) >= 2 and all(1 <= len(g.split()) <= 5 and not re.search(r'[:.?]$', g) for g in segs):
                    return True          # First Last; First Last
                return bool(pres) and pres.split(' and ')[0] in x.lower()   # the presenter's own name starts the list
            j = next((k for k in range(1, len(head)) if authorish(k)), len(head))
            title = tidy(' '.join(head[:j]))
            out.append(dict(student=tidy(l.split(':', 1)[1]), title=title, mentors=split_people(mentor),
                            authors=tidy(' '.join(head[j:])), page=pno))
    return out

def parse_2026(path, src):
    """TITLE: / PRESENTER: / MENTOR: / CONTRIBUTING AUTHORS: blocks, in capitals."""
    out = []
    pages = pdftext(path).split('\f')
    for pno, page in enumerate(pages, 1):
        for blk in re.split(r'\n(?=TITLE:)', '\n' + page):
            if 'TITLE:' not in blk: continue
            def field(name, nxt):
                m = re.search(name + r':?\s*(.*?)(?=\n(?:' + nxt + r')|\n\n|$)', blk, re.S)
                return tidy(m.group(1).replace('\n', ' ')) if m else ''
            title = field('TITLE', 'PRESENTER')
            student = field('PRESENTER', 'MENTOR|CONTRIBUTING')
            m = re.search(r'\nMENTORS?:?[ \t]*(.*?)(?=\nCONTRIBUTING|\n\n|\n[A-Z][a-z]|$)', blk, re.S)
            mentor = tidy(m.group(1).replace('\n', ' ')) if m else ''
            authors = field('CONTRIBUTING AUTHORS', r'[A-Z][a-z]')
            mentor = re.sub(r'\b(DR\.?|PHD|MD)\s*', '', mentor).strip()
            out.append(dict(student=smart_case(student), title=title, mentors=split_people(mentor), authors=authors,
                            page=pno))
    return out

def parse_table(path, src):
    """The Summer symposium page: one row per presentation, columns
    student first, student last, type, mentor first, mentor last, title, ..."""
    t = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'Summer\s+(20\d\d)\s+Symposium', t)
    year = int(m.group(1)) if m else None
    out = []
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S | re.I):
        cells = [tidy(re.sub(r'<[^>]+>', ' ', c)) for c in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)]
        if len(cells) < 6 or not re.search(r'present', cells[2], re.I): continue
        mf, ml = cells[3], cells[4]
        # usually first and last name; sometimes a full name in each (two mentors)
        ment = [mf, ml] if len(mf.split()) >= 2 and len(ml.split()) >= 2 else split_people(mf + ' ' + ml)
        out.append(dict(student=tidy(cells[0] + ' ' + cells[1]), title=cells[5], mentors=ment, authors='', page=''))
    return out, year

PARSERS = {'pdf2021': parse_2021, 'pdf2026': parse_2026}


# ---------------------------------------------------------------- titles
def fix_title(title, student):
    t = tidy(title)
    # a tail of the student's name stuck to the front ('ohee Kang Effects of ...')
    for k in range(1, len(student)):
        frag = student[k:]
        if len(frag) >= 4 and t.startswith(frag + ' '):
            t = t[len(frag) + 1:]
            break
    # the title repeated, cut short, at the end ('... Erythrocytes eological Properties of')
    for n in range(len(t) // 2, 7, -1):
        tail = t[-n:].strip()
        if len(tail) >= 8 and t.find(tail) < n and t.find(tail) != len(t) - n:
            t = t[:len(t) - n].strip()
            break
    return t


# ---------------------------------------------------------------- build
def read_atlas(path):
    t = open(path, encoding='utf-8').read()
    m = re.search(r'<script id="atlasdata" type="application/json">(.*?)</script>', t, re.S)
    data = json.loads(m.group(1))
    pis = [dict(id=i, n=p['n']) for i, p in enumerate(data['pis'])]
    m = re.search(r'<script id="surehist" type="application/json">(.*?)</script>', t, re.S)
    return pis, data.get('vocab', []), (json.loads(m.group(1)) if m else {'mentors': []}), t

def fetch(cache):
    os.makedirs(cache, exist_ok=True)
    for s in SOURCES:
        dest = os.path.join(cache, s['file'])
        req = urllib.request.Request(s['url'], headers={'User-Agent': 'LabAtlas symposium scraper'})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, 'wb') as f:
            f.write(r.read())
        print('fetched', s['url'], '->', dest, file=sys.stderr)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--atlas', required=True, help='the atlas HTML: investigators and the previous records')
    ap.add_argument('--cache', default='build/symposia', help='where the fetched books live')
    ap.add_argument('--fetch', action='store_true', help='download the Emory-hosted books first')
    ap.add_argument('--ref-year', type=int, default=None, help='"recent" means within 3 years of this (default: newest book)')
    ap.add_argument('--out', default='build/surehist.json')
    ap.add_argument('--report', default=None)
    ap.add_argument('--write-atlas', action='store_true', help='splice the result into --atlas in place')
    ap.add_argument('--keep-students', action='store_true',
                    help='keep presenting students\' names in the output (default: left out; the page shows a count)')
    ap.add_argument('--legacy-cache', default=None,
                    help='the 2007-2019 records with student names, kept outside the page (default: <cache>/legacy_records.json)')
    a = ap.parse_args()
    a.legacy_cache = a.legacy_cache or os.path.join(a.cache, 'legacy_records.json')

    pis, vocab, old, page = read_atlas(a.atlas)
    names = Names(pis, vocab)
    if a.fetch: fetch(a.cache)

    # 1. the books parsed fresh
    fresh, replaced, srcmeta = [], set(), {}
    for s in SOURCES:
        path = os.path.join(a.cache, s['file'])
        if not os.path.exists(path):
            print('missing', path, '(run with --fetch); its old records are kept', file=sys.stderr)
            continue
        if s['kind'] == 'table':
            recs, y = parse_table(path, s)
        else:
            recs, y = PARSERS[s['kind']](path, s), s['y']
        y = y or s['y']
        label = s['label'].format(y=y)
        replaced.update(r.format(y=y) for r in s['replaces'])
        srcmeta[label] = s['url']
        for r in recs:
            r.update(y=y, term=s['term'], program=s['program'], source=label, url=s['url'], book=True)
            for m in r['mentors']: names.learn(m, faculty=True)
            for st in split_people(r['student']): names.learn(st, student=True)
        fresh += recs
        print('%-34s %4d presentations' % (label, len(recs)), file=sys.stderr)

    # 2. the old records, from books that were not parsed fresh. The page no
    #    longer carries students' names, so the full records are kept in a local
    #    cache (never published); a page that still has the names refreshes it.
    has_names = any(r.get('student') for m in old.get('mentors', []) for r in m.get('records', []))
    if not has_names and os.path.exists(a.legacy_cache):
        old = json.load(open(a.legacy_cache, encoding='utf-8'))
        print('old records from', a.legacy_cache, file=sys.stderr)
    elif has_names:
        os.makedirs(os.path.dirname(os.path.abspath(a.legacy_cache)), exist_ok=True)
        json.dump({'mentors': old.get('mentors', [])}, open(a.legacy_cache, 'w', encoding='utf-8'), ensure_ascii=False)
    else:
        print('note: no student names in the page and no', a.legacy_cache, '- the checks that compare mentors with '
              'students are skipped for the old records', file=sys.stderr)
    legacy = collections.defaultdict(lambda: dict(mentors=[]))
    for m in old.get('mentors', []):
        for r in m.get('records', []):
            src = r.get('source', '')
            if src in replaced or src in srcmeta or src.startswith('news_'): continue
            k = (src, r.get('y'), r.get('student', ''), r.get('title', '')) if (r.get('student') or r.get('title')) else (src, r.get('y'), id(r))
            L = legacy[k]
            L.update(y=r.get('y'), term=r.get('term'), program=r.get('program'), student=tidy(r.get('student', '')),
                     title=r.get('title', ''), page=r.get('page', ''), source=LEGACY.get(src, src),
                     url=r.get('url') or (ISSUU + src if src in LEGACY else ''), book=False, ns=r.get('ns'))
            L['mentors'].append(m['name'])
            if L['student']:
                for st in split_people(L['student']): names.learn(st, student=True)
    # in the old records, someone named as the only mentor of a project is faculty
    for L in legacy.values():
        ok = [nm for m in dict.fromkeys(L['mentors']) for nm, _ in clean_names(m, names, True) if nm]
        if len(ok) == 1 and key(ok[0]) not in names.students: names.learn(ok[0], faculty=True)

    # 3. decide who mentored what
    log = collections.defaultdict(list)
    people = {}
    def person(display, pid):
        k = ('pi', pid) if pid is not None else ('name', key(display))
        if k not in people:
            people[k] = dict(name=pis[pid]['n'] if pid is not None else display, pi_id=pid, records=[])
        return people[k]

    for r in fresh + list(legacy.values()):
        raw = list(dict.fromkeys(r['mentors']))
        if not raw and r.get('authors'):
            # no mentor printed: the last author who is known faculty, if any
            for au in reversed(r['authors'].split(';')):
                if ',' not in au: continue
                ln, fn = [x.strip() for x in au.split(',', 1)]
                cand = smart_case(fn + ' ' + ln)
                if names.known(cand):
                    raw = [cand]; log['mentor taken from the author list (none printed)'].append(cand); break
            else:
                log['dropped: no mentor printed and no known faculty among the authors'].append(r['title'][:90])
        elif not raw:
            log['dropped: no mentor printed and no author list'].append(r['title'][:90])
        cleaned = []
        for m in raw:
            for nm, why in clean_names(m, names, strict=not r['book']):
                if nm is None:
                    log['dropped: ' + why].append(m); continue
                if why: log[why].append('%s -> %s' % (m, nm))
                cleaned.append(nm)
        # co-authors listed with known faculty are not mentors (old records only;
        # a book that names the faculty mentor is taken at its word)
        if not r['book'] and len(cleaned) > 1:
            fac = [c for c in cleaned if names.known(c)]
            if fac:
                for c in cleaned:
                    if c not in fac: log['dropped: co-author listed beside known faculty'].append(c)
                cleaned = fac
        studs = [fold(x).lower() for x in split_people(r['student'])]
        stud_keys = {key(x) for x in studs}
        title = fix_title(r['title'], r['student'])
        if title != tidy(r['title']): log['title repaired'].append(title[:90])
        for c in dict.fromkeys(cleaned):
            k = key(c)
            cl = fold(c).lower()
            if k in stud_keys or any(same_person(c, x) for x in studs) or \
                    (not r['book'] and k in names.students and not names.known(c)) or \
                    any(len(x) >= 6 and (cl.startswith(x + ' ') or cl.endswith(x)) for x in studs):
                log['dropped: the presenting student, not a mentor'].append(None); continue
            pid, how = names.match(c)
            if how in ('nickname', 'spelling', 'hyphen', 'longer or shorter first name'): log['matched to atlas by ' + how].append('%s -> %s' % (c, pis[pid]['n']))
            P = person(c, pid)
            rec = dict(y=r['y'], term=r['term'], program=r['program'], student=r['student'], title=title,
                       source=r['source'], page=r['page'],
                       ns=len(split_people(r['student'])) if r['student'] else (r.get('ns') or 1))
            if r.get('url'): rec['url'] = r['url']
            if rec not in P['records']: P['records'].append(rec)

    # 4. one entry per person: spelling variants, nicknames and short forms of
    #    the same name (same surname) are merged, into the atlas match if there is one
    groups = collections.defaultdict(list)
    for k, P in people.items():
        t = tokens(P['name'])
        if len(t) >= 2: groups[t[-1].split('-')[0]].append(k)
    for g in groups.values():
        g.sort(key=lambda k: (people[k]['pi_id'] is None, -len(people[k]['records']), -len(people[k]['name'])))
        for i, ki in enumerate(g):
            if ki not in people: continue
            for kj in g[i + 1:]:
                if kj not in people or people[kj]['pi_id'] is not None: continue
                if same_first(tokens(people[ki]['name'])[0], tokens(people[kj]['name'])[0]):
                    log['merged as the same person'].append('%s + %s' % (people[ki]['name'], people[kj]['name']))
                    for rec in people.pop(kj)['records']:
                        if rec not in people[ki]['records']: people[ki]['records'].append(rec)

    # 5. shape it for the page
    ref = a.ref_year or max([r['y'] for r in fresh] + [r.get('y') or 0 for r in legacy.values()] + [0])
    mentors = []
    for P in people.values():
        recs = sorted(P['records'], key=lambda r: (-r['y'], r['title'], r['student']))
        studs = set()
        for r in recs:
            ss = split_people(r['student']) if r['student'] else ['#%d.%d' % (id(r), i) for i in range(r['ns'])]
            studs.update(key(s) or s for s in ss)
        if not a.keep_students:
            for r in recs: r.pop('student', None)
        mentors.append(dict(name=P['name'], pi_id=P['pi_id'], programs=sorted({r['program'] for r in recs}),
                            years=sorted({r['y'] for r in recs}), n_students=len(studs), records=recs))
    mentors.sort(key=lambda m: (-m['n_students'], m['name']))
    hist = {}
    for m in mentors:
        if m['pi_id'] is None: continue
        ys = m['years']
        hist[str(m['pi_id'])] = dict(y=ys, t=sorted({r['term'] for r in m['records']}), n=len(m['records']),
                                     tier='RECENT' if ys[-1] >= ref - 3 else 'PAST',
                                     sure=any(r['program'] == 'SURE' for r in m['records']), records=m['records'])
    out = dict(ref_year=ref, pis=hist, mentors=mentors,
               source_caveat='From Emory undergraduate research symposium abstract books: 2021 and 2026 read from '
                             'the books themselves, 2007-2019 from the Issuu editions\' text layer with every mentor '
                             'name checked. Mentors matched to atlas investigators by name.')
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('%d mentors (%d in the atlas), %d records' % (len(mentors), len(hist), sum(len(m['records']) for m in mentors)),
          file=sys.stderr)

    if a.report:
        oldm = old.get('mentors', [])
        with open(a.report, 'w', encoding='utf-8') as f:
            f.write('# Symposium mentors: rebuild report\n\n')
            f.write('| | before | after |\n|---|---|---|\n')
            f.write('| mentors | %d | %d |\n' % (len(oldm), len(mentors)))
            f.write('| matched to an atlas investigator | %d | %d |\n' % (sum(m.get('pi_id') is not None for m in oldm), len(hist)))
            f.write('| project records | %d | %d |\n\n' % (sum(len(m['records']) for m in oldm), sum(len(m['records']) for m in mentors)))
            f.write('Records are counted once per mentor they are listed under, so "before" includes a copy for every '
                    'fragment and co-author name that sat in a mentor slot.\n\n')
            f.write('Students\' names are not listed here or published in the page.\n\n')
            for k in sorted(log):
                if all(x is None for x in log[k]):
                    f.write('## %s (%d)\n\nNames not listed.\n\n' % (k, len(log[k]))); continue
                v = list(dict.fromkeys(log[k]))
                f.write('## %s (%d)\n\n' % (k, len(v)))
                f.writelines('- %s\n' % x for x in sorted(v))
                f.write('\n')
        print('report ->', a.report, file=sys.stderr)

    if a.write_atlas:
        blob = json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        new, n = re.subn(r'(<script id="surehist" type="application/json">)(.*?)(</script>)',
                         lambda m: m.group(1) + blob + m.group(3), page, count=1, flags=re.S)
        assert n == 1, 'no surehist block in the atlas'
        open(a.atlas, 'w', encoding='utf-8').write(new)
        print('wrote', a.atlas, file=sys.stderr)

if __name__ == '__main__':
    main()
