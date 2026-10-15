"""Name handling shared by the PubMed publication scripts: split an atlas name into surname and given names,
and build the PubMed query (full name with a wildcard, so any middle initial matches, AND an Emory-family
affiliation)."""
import re, unicodedata
AFF = '(Emory[ad] OR "Children\'s Healthcare of Atlanta"[ad] OR Yerkes[ad] OR Winship[ad])'
SUFFIX = {'jr', 'jr.', 'sr', 'sr.', 'ii', 'iii', 'iv', 'md', 'phd'}
PART = {'van', 'von', 'de', 'del', 'della', 'da', 'di', 'la', 'le', 'du', 'dos', 'das', 'bin', 'al', 'el', 'ter', 'den', 'der'}
def ascii_(s): return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
def parts(name):
    nick = re.findall(r'\(([^)]+)\)', name)
    n = re.sub(r'\([^)]*\)|"[^"]*"', ' ', name)
    toks = [t for t in re.split(r'\s+', n.replace(',', ' ').strip()) if t]
    while toks and toks[-1].lower().strip('.') in {x.strip('.') for x in SUFFIX}: toks.pop()
    if len(toks) < 2: return None
    # surname: last token plus any lowercase particles before it
    k = len(toks) - 1
    while k - 1 > 0 and toks[k-1].lower() in PART: k -= 1
    last = ' '.join(toks[k:]); given = toks[:k]
    first = given[0]
    if re.fullmatch(r'[A-Za-z]\.?', first) and len(given) > 1:      # "A. Alfred Chahine" -> "A Alfred"
        first = first.strip('.') + ' ' + given[1]
    firsts = [first.strip('.')] + [x.strip() for x in nick]
    return last, firsts
def query(name):
    pr = parts(name)
    if not pr: return None
    last, firsts = pr
    names_ = []
    for f in firsts:
        for L in {last, ascii_(last)}:
            for F in {f, ascii_(f)}:
                names_.append('%s, %s*[FAU]' % (L, F))
    return '(' + ' OR '.join(sorted(set(names_))) + ') AND ' + AFF
