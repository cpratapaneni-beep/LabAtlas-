"""Wet/dry lab classifier for the Emory Lab Atlas, trained on hand-checked labels.

The atlas used to place every investigator on the wet/dry axis with a
hand-weighted keyword score (model v3.1). This module replaces it with a model
fitted to a gold set of 800 investigators labelled by reading their records
(see LABELLING_RUBRIC.md). Half of the gold set trains the model; the other
half is locked away and only ever used by `evaluate`.

What the model reads, per investigator:
  * every publication title on the record (the main signal),
  * the profile text, grant titles, departments/centres and degrees.

How it decides:
  1. A title model scores each publication title for bench-lab wording. It is
     trained on the titles of gold wet investigators (target 1) and gold dry
     investigators (target 0), each person's titles weighted so a prolific
     author counts once, not once per paper.
  2. A context model scores the profile, grants, departments and degrees.
  3. A small stacking model turns the per-title scores (mean, upper quartile,
     share above 0.5, count) and the context score into P(wet). Hybrid gold
     labels enter as half wet, half dry.
  4. P(wet) is cut into five states: wet, leans wet, hybrid, leans dry, dry.
     A record with no titles, no grants and too little profile text to judge
     is left unclassified instead of guessed at.

Stages 1-2 feed stage 3 with out-of-fold scores, so the stacker never sees a
score produced by a model that was trained on the same person.

Usage (from the repository root):
  python ml/wetdry.py cv       --data atlas.html --split ml/split.json --labels ml/gold_labels.csv
  python ml/wetdry.py evaluate --data atlas.html --split ml/split.json --labels ml/gold_labels.csv --out ml/report
  python ml/wetdry.py predict  --data atlas.html --split ml/split.json --labels ml/gold_labels.csv --out predictions.json

`--data` accepts either the atlas JSON or the atlas HTML file itself.
Needs numpy, scipy and scikit-learn.
"""
import argparse
import csv
import json
import math
import os
import re
import sys

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

MODEL_VERSION = 'wd-2026.09'
SEED = 20260925
USE_LEX = True
# self-training thresholds on P(wet) for unlabelled records, and their weight
PSEUDO = (0.90, 0.02)
PSEUDO_WEIGHT = 0.3

# P(wet) bands. Chosen by cross-validation on the training half only (see `cv`).
BANDS = {'wet': 0.70, 'lean_wet': 0.45, 'lean_dry': 0.30, 'dry': 0.02}

STATE = {'none': 0, 'wet': 1, 'dry': 2, 'hybrid': 3, 'lean_wet': 4, 'lean_dry': 5}
SIDE = {0: None, 1: 'W', 4: 'W', 2: 'D', 5: 'D', 3: 'H'}


# ---------------------------------------------------------------- data access
def load_data(path):
    txt = open(path, encoding='utf-8').read()
    if path.lower().endswith(('.html', '.htm')):
        m = re.search(r'<script[^>]*id="atlasdata"[^>]*>(.*?)</script>', txt, re.S)
        if not m:
            sys.exit('no <script id="atlasdata"> in ' + path)
        txt = m.group(1)
    return json.loads(txt)


def load_gold(labels_path, split_path, D=None):
    """gold[person_index] = 'W'|'H'|'D'|'U', plus the train/test index sets.

    The labels point at people by their position in the data. If the file
    carries names and the data is given, every one is checked, so a re-scraped
    or re-ordered atlas cannot silently pin a label on the wrong person."""
    split = json.load(open(split_path))
    order = split['order']
    gold, wrong = {}, []
    for r in csv.DictReader(open(labels_path, encoding='utf-8')):
        i = order[int(r['code'][1:])]
        if D is not None and r.get('name') and (i >= len(D['pis']) or D['pis'][i]['n'] != r['name']):
            wrong.append(r['code'])
        gold[i] = r['label']
    if wrong:
        sys.exit('%d gold labels no longer point at the person they were given to (%s ...); '
                 'the data has changed order since labelling' % (len(wrong), ', '.join(wrong[:5])))
    return gold, set(split['train']), set(split['test'])


# boilerplate that says nothing about the method of the underlying work
_TITLE_NOISE = re.compile(
    r'^(abstract\s+[a-z]*\d+[a-z]?\s*:|faculty opinions recommendation of|'
    r'(supplementary|supplemental)\s+\w+( \w+)? from|table s\d+ from|figure s\d+ from|'
    r'movie s\d+ from|data s\d+ from|correction( to)?:|erratum( to)?:|'
    r'corrigendum( to)?|publisher correction:|author correction:)\s*', re.I)
_CODE = re.compile(r'^[#]?\s*[a-z]{0,6}[- ]?\d{1,5}[a-z]?[.:]\s+', re.I)


def clean_title(t):
    t = str(t or '').strip()
    for _ in range(2):
        t = _TITLE_NOISE.sub('', t)
        t = _CODE.sub('', t)
    return t.lower()


def titles_of(p, raw=False):
    """Cleaned, de-duplicated titles; with raw=True, the original wording of each."""
    out, seen = [], set()
    for e in p.get('p') or []:
        r = str(e[0] if isinstance(e, list) else e or '').strip()
        t = clean_title(r)
        if len(t) >= 12 and t not in seen:
            seen.add(t)
            out.append(r if raw else t)
    return out


# a profile made of a patient's review says nothing about the lab
_REVIEW = re.compile(r"\b(my (doctor|wife|husband|son|daughter|pcp|visit)|i (was|had|have|felt|needed)|"
                     r"highly recommend|recommend (him|her|dr)|listens? to me|made me feel)\b", re.I)


def bio_of(p):
    b = str(p.get('b') or '')
    return '' if _REVIEW.search(b) else b


def context_text(p, D):
    units = [str(D['depts'][j].get('n', '')) for j in p.get('d') or [] if j < len(D['depts'])]
    insts = [str(D['insts'][j].get('k', '')) for j in p.get('i') or [] if j < len(D['insts'])]
    kw = []
    for t in p.get('t') or []:
        kw.extend(t if isinstance(t, list) else [t])
    deg = str(p.get('g') or '')
    parts = [bio_of(p), ' '.join(p.get('gn') or []), ' '.join(kw),
             ' '.join('unit_' + re.sub(r'\W+', '_', u.lower()) for u in units),
             ' '.join('inst_' + i.lower() for i in insts),
             ' '.join('deg_' + d.lower() for d in re.findall(r'[A-Za-z]+', deg))]
    return ' '.join(x for x in parts if x)


def degree_flags(p):
    g = ' ' + re.sub(r'[^a-z]+', ' ', str(p.get('g') or '').lower()) + ' '
    has = lambda *ks: float(any(' ' + k + ' ' in g for k in ks))
    phd, md = has('phd'), has('md', 'mbbs', 'do')
    return [phd, md, phd * (1 - md), has('rn', 'dnp', 'msn', 'bsn', 'aprn', 'cnm', 'np', 'fnp'),
            has('dds', 'dmd'), has('psyd', 'abpp'), has('mph', 'msph', 'dsc')]


# Prior knowledge: word lists that mark a title as bench, computational or clinical.
# They add a little robustness for words too rare in the gold set to be learned.
LEX = {
    'organism': r"\b(mice|mouse|murine|rats?|rodents?|zebrafish|drosophila|elegans|primates?|macaques?|rhesus|"
                r"marmosets?|ferrets?|hamsters?|porcine|swine|piglets?|xenografts?|transgenic|knockout|knock-in|"
                r"organoids?|in vivo|in vitro|ex vivo|cell lines?|yeast|saccharomyces|embryos?|ipsc|"
                r"stem cells?|cultured|explants?|lampreys?|nematodes?|voles?|songbirds?|bacteria|bacterial)\b",
    'bench': r"\b(proteins?|crystal structures?|cryo-?em|structural basis|binding|enzymes?|enzymatic|kinases?|"
             r"phosphorylation|signal(l)?ing|receptors?|mutagenesis|synthesis|synthetic|catalys[ie]s|catalytic|"
             r"spectroscop\w*|mass spectrometr\w*|western|pcr|antibod(y|ies)|t cells?|b cells?|macrophages?|"
             r"neurons?|mitochondri\w*|transcription factors?|chromatin|histones?|ligands?|inhibitors?|"
             r"nanoparticles?|hydrogels?|biomaterials?|scaffolds?|peptides?|glycans?|replication|virions?|"
             r"plasmids?|crispr|electrophysiolog\w*|patch-clamp|imaging agents?|radioligands?|probes?|"
             r"assays?|purification|recombinant|mechanism|mechanisms|pathway|pathways)\b",
    'comp': r"\b(algorithms?|software|computational|machine learning|deep learning|neural networks?|"
            r"statistical|bayesian|simulations?|in silico|bioinformatic\w*|genome-wide association|gwas|"
            r"mendelian randomization|polygenic|language models?|llms?|segmentation|radiomics?|"
            r"natural language|data science|framework for|r package|estimat(ion|ing|or))\b",
    'clinic': r"\b(patients?|cohort|trials?|randomi[sz]ed|retrospective|case reports?|case series|surveys?|"
              r"outcomes|clinical|registry|meta-analysis|systematic review|qualitative|disparit\w+|"
              r"screening|veterans|residents?|residency|students|education|quality improvement|"
              r"implementation|nursing|caregivers?|adolescents|women|children|infants|emergency department|"
              r"hospital\w*|surgery|surgical|guidelines?|consensus|policy|epidemiolog\w*|prevalence|"
              r"incidence|mortality|risk factors?)\b",
}
LEX_RE = {k: re.compile(v) for k, v in LEX.items()}


def lexicon_rates(ts):
    """Share of a person's titles that use each word list."""
    if not ts:
        return [0.0] * len(LEX_RE)
    return [sum(1 for t in ts if r.search(t)) / len(ts) for r in LEX_RE.values()]


def evidence(p):
    return len(titles_of(p)), len(p.get('gn') or []), len(bio_of(p))


# -------------------------------------------------------------------- models
def _tfidf(min_df=2):
    return TfidfVectorizer(ngram_range=(1, 2), min_df=min_df, max_df=0.5, sublinear_tf=True,
                           token_pattern=r'(?u)\b[a-z][a-z0-9\-]{1,}\b', dtype=np.float32)


class Vectors:
    """Fits the vocabularies once on every record's text (no labels involved)."""

    def __init__(self, D):
        P = D['pis']
        self.titles = [titles_of(p) for p in P]
        self.ctx = [context_text(p, D) for p in P]
        self.tv = _tfidf(2).fit([t for ts in self.titles for t in ts])
        self.cv = _tfidf(2).fit(self.ctx)
        self.Xctx = self.cv.transform(self.ctx)
        # title matrix, row per title, with owner index
        rows, owner = [], []
        for i, ts in enumerate(self.titles):
            rows.extend(ts)
            owner.extend([i] * len(ts))
        self.Xt = self.tv.transform(rows) if rows else csr_matrix((0, 0))
        self.owner = np.array(owner, dtype=np.int64)
        self.by_person = [[] for _ in P]
        for r, i in enumerate(owner):
            self.by_person[i].append(r)
        self.deg = np.array([degree_flags(p) for p in P], dtype=np.float32)
        self.ngrant = np.array([len(p.get('gn') or []) for p in P], dtype=np.float32)
        self.nbio = np.array([len(bio_of(p)) for p in P], dtype=np.float32)
        self.lex = np.array([lexicon_rates(ts) for ts in self.titles], dtype=np.float32)


def _target(lbl):
    return {'W': 1.0, 'D': 0.0, 'H': 0.5}.get(lbl)


def fit_title_model(V, people, gold, C=4.0, pseudo=None):
    rows, y, w = [], [], []
    for i in people:
        t = _target(gold[i])
        if t is None or t == 0.5 or not V.by_person[i]:
            continue
        r = V.by_person[i]
        rows.extend(r)
        y.extend([int(t)] * len(r))
        w.extend([1.0 / math.sqrt(len(r))] * len(r))
    # confidently scored unlabelled people, at reduced weight (self-training)
    for i, t in (pseudo or {}).items():
        r = V.by_person[i]
        rows.extend(r)
        y.extend([t] * len(r))
        w.extend([PSEUDO_WEIGHT / math.sqrt(len(r))] * len(r))
    y, w = np.array(y), np.array(w)
    # give the two sides equal total weight so the rarer wet class is not drowned out
    for c in (0, 1):
        m = y == c
        if m.any():
            w[m] *= (w.sum() / 2.0) / w[m].sum()
    w *= len(w) / w.sum()
    m = LogisticRegression(C=C, max_iter=3000)
    m.fit(V.Xt[rows], y, sample_weight=w)
    return m


def fit_ctx_model(V, people, gold, C=2.0):
    idx, y, w = [], [], []
    for i in people:
        t = _target(gold[i])
        if t is None:
            continue
        if t == 0.5:
            idx += [i, i]; y += [1, 0]; w += [0.5, 0.5]
        else:
            idx.append(i); y.append(int(t)); w.append(1.0)
    m = LogisticRegression(C=C, max_iter=3000, class_weight='balanced')
    m.fit(V.Xctx[idx], np.array(y), sample_weight=np.array(w))
    return m


def title_agg(V, tm, people):
    """Per-person summary of the title scores."""
    out = np.zeros((len(people), 5), dtype=np.float32)
    all_rows = [r for i in people for r in V.by_person[i]]
    pr = tm.predict_proba(V.Xt[all_rows])[:, 1] if all_rows else np.array([])
    k = 0
    for n, i in enumerate(people):
        m = len(V.by_person[i])
        if m:
            s = np.sort(pr[k:k + m])
            k += m
            q = s[int(0.75 * (m - 1)):]
            out[n] = [s.mean(), q.mean(), (s > 0.5).mean(), math.log1p(m), 1.0]
    return out


def _logit(x):
    x = np.clip(x, 1e-4, 1 - 1e-4)
    return np.log(x / (1 - x))


def stack_features(V, tm, cm, people):
    """Stacking features for people who have at least one title."""
    ta = title_agg(V, tm, people)
    cp = cm.predict_proba(V.Xctx[people])[:, 1]
    feats = [_logit(ta[:, 0:1]), _logit(ta[:, 1:2]), ta[:, 2:3], ta[:, 3:4],
             _logit(cp)[:, None], np.log1p(V.ngrant[people])[:, None], V.deg[people]]
    if USE_LEX:
        feats.append(V.lex[people])
    return np.hstack(feats)


def oof_stack(V, people, gold, folds=5, seed=SEED, pseudo=None):
    """Out-of-fold stacking features for titled labelled people, and out-of-fold
    context scores for every labelled person (used to calibrate the context model)."""
    people = [i for i in people if _target(gold[i]) is not None]
    ylab = np.array([gold[i] for i in people])
    titled = np.array([len(V.by_person[i]) > 0 for i in people])
    X, ctx = None, np.zeros(len(people))
    skf = StratifiedKFold(folds, shuffle=True, random_state=seed)
    for tr, te in skf.split(people, ylab):
        trp = [people[j] for j in tr]
        tm, cm = fit_title_model(V, trp, gold, pseudo=pseudo), fit_ctx_model(V, trp, gold)
        ctx[te] = cm.predict_proba(V.Xctx[[people[j] for j in te]])[:, 1]
        tt = [j for j in te if titled[j]]
        if not tt:
            continue
        f = stack_features(V, tm, cm, [people[j] for j in tt])
        if X is None:
            X = np.zeros((len(people), f.shape[1]), dtype=np.float32)
        X[tt] = f
    keep = np.where(titled)[0]
    return [people[j] for j in keep], X[keep], people, ctx


def _soft_fit(X, labs, C):
    """Logistic fit with hybrid labels counted half wet, half dry. No class
    re-weighting, so the output stays a calibrated probability."""
    Xs, y, w = [], [], []
    for x, l in zip(X, labs):
        t = _target(l)
        if t == 0.5:
            Xs += [x, x]; y += [1, 0]; w += [0.5, 0.5]
        else:
            Xs.append(x); y.append(int(t)); w.append(1.0)
    m = LogisticRegression(C=C, max_iter=3000)
    m.fit(np.array(Xs), np.array(y), sample_weight=np.array(w))
    return m


class Model:
    def __init__(self, V, people, gold, bands=None):
        self.V = V
        self.bands = dict(bands or BANDS)
        lab = [i for i in people if _target(gold[i]) is not None]
        self.pseudo = None
        self._fit(lab, gold, None)
        if PSEUDO:
            # self-training: score every titled record nobody labelled, keep the
            # confident ones, and refit with them at reduced weight. Every gold
            # record, trained on or held out, is kept out of the pool.
            pool = [i for i in range(len(V.by_person)) if V.by_person[i] and i not in gold]
            P, _ = self.proba(pool)
            self.pseudo = {i: int(p >= 0.5) for i, p in zip(pool, P) if p >= PSEUDO[0] or p <= PSEUDO[1]}
            self._fit(lab, gold, self.pseudo)

    def _fit(self, lab, gold, pseudo):
        V = self.V
        self.tm = fit_title_model(V, lab, gold, pseudo=pseudo)
        self.cm = fit_ctx_model(V, lab, gold)
        pp, X, allp, ctx = oof_stack(V, lab, gold, pseudo=pseudo)
        self.st = _soft_fit(X, [gold[i] for i in pp], C=0.5)
        # maps the (class-balanced) context score to a calibrated P(wet)
        self.cal = _soft_fit(_logit(ctx)[:, None], [gold[i] for i in allp], C=1.0)

    def proba(self, people):
        """P(wet) for each person, and whether it came from titles or profile only."""
        people = list(people)
        P = np.zeros(len(people))
        titled = [n for n, i in enumerate(people) if self.V.by_person[i]]
        bare = [n for n, i in enumerate(people) if not self.V.by_person[i]]
        if titled:
            X = stack_features(self.V, self.tm, self.cm, [people[n] for n in titled])
            P[titled] = self.st.predict_proba(X)[:, 1]
        if bare:
            c = self.cm.predict_proba(self.V.Xctx[[people[n] for n in bare]])[:, 1]
            P[bare] = self.cal.predict_proba(_logit(c)[:, None])[:, 1]
        return P, set(bare)

    def states(self, people):
        people = list(people)
        P, bare = self.proba(people)
        out = []
        for n, i in enumerate(people):
            # banded at the precision it is stored and shown at, so the state and
            # the printed P(wet) can never disagree at a band edge
            p = round(float(P[n]), 3)
            if n in bare:
                # no titles: grants or a real profile are needed, and then only a clear call
                enough = self.V.ngrant[i] > 0 or self.V.nbio[i] >= 200
                if not enough:
                    out.append((0, p, 'no publications, grants or profile text'))
                    continue
                if self.bands['dry'] < p < self.bands['wet']:
                    out.append((0, p, 'profile only, and it does not settle the question'))
                    continue
            out.append((band(p, self.bands), p, None))
        return out


def band(p, b):
    if p >= b['wet']:
        return STATE['wet']
    if p >= b['lean_wet']:
        return STATE['lean_wet']
    if p <= b['dry']:
        return STATE['dry']
    if p <= b['lean_dry']:
        return STATE['lean_dry']
    return STATE['hybrid']


# ------------------------------------------------------------------- scoring
def score(pairs):
    """pairs: [(gold 'W'|'H'|'D'|'U', predicted state int)]. Returns a dict of metrics."""
    sc = [(g, SIDE[s]) for g, s in pairs if g in 'WHD']
    n = len(sc)
    cov = [x for x in sc if x[1] is not None]
    acc_all = sum(g == s for g, s in sc) / n if n else float('nan')
    acc_cov = sum(g == s for g, s in cov) / len(cov) if cov else float('nan')
    f1 = []
    for c in 'WHD':
        tp = sum(g == c and s == c for g, s in sc)
        fp = sum(g != c and s == c for g, s in sc)
        fn = sum(g == c and s != c for g, s in sc)
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        f1.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    wtp = sum(g == 'W' and s == 'W' for g, s in sc)
    wfp = sum(g != 'W' and s == 'W' for g, s in sc)
    wfn = sum(g == 'W' and s != 'W' for g, s in sc)
    u = [(g, s) for g, s in pairs if g == 'U']
    return {
        'n_scored': n,
        'coverage': len(cov) / n if n else float('nan'),
        'accuracy_all': acc_all,
        'accuracy_when_placed': acc_cov,
        'macro_f1': sum(f1) / 3,
        'f1_W': f1[0], 'f1_H': f1[1], 'f1_D': f1[2],
        'wet_precision': wtp / (wtp + wfp) if wtp + wfp else float('nan'),
        'wet_recall': wtp / (wtp + wfn) if wtp + wfn else float('nan'),
        'unclear_left_unclassified': (sum(1 for g, s in u if s == 0) / len(u)) if u else float('nan'),
        'n_unclear': len(u),
    }


def bootstrap(pairs, key, n=2000, seed=SEED):
    rng = np.random.default_rng(seed)
    pairs = list(pairs)
    vals = []
    for _ in range(n):
        smp = [pairs[j] for j in rng.integers(0, len(pairs), len(pairs))]
        v = score(smp)[key]
        if not math.isnan(v):
            vals.append(v)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def bootstrap_diff(pa, pb, key, n=2000, seed=SEED):
    """CI for score(pa)[key] - score(pb)[key], resampling the same people."""
    rng = np.random.default_rng(seed)
    m = len(pa)
    vals = []
    for _ in range(n):
        ix = rng.integers(0, m, m)
        a = score([pa[j] for j in ix])[key]
        b = score([pb[j] for j in ix])[key]
        if not (math.isnan(a) or math.isnan(b)):
            vals.append(a - b)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


V31_STATE = lambda p: int(p.get('l') or 0)


# ---------------------------------------------------------------- commands
def cmd_cv(a):
    D = load_data(a.data)
    gold, train, _ = load_gold(a.labels, a.split, D)
    V = Vectors(D)
    tr = sorted(train)
    labs = np.array([gold[i] for i in tr])
    res_new, res_old = [], []
    for rep in range(a.repeats):
        skf = StratifiedKFold(5, shuffle=True, random_state=SEED + rep)
        for f_tr, f_te in skf.split(tr, labs):
            ptr = [tr[j] for j in f_tr]
            pte = [tr[j] for j in f_te]
            m = Model(V, ptr, gold)
            st = m.states(pte)
            res_new += [(gold[i], s[0]) for i, s in zip(pte, st)]
            res_old += [(gold[i], V31_STATE(D['pis'][i])) for i in pte]
    print('cross-validated on the training half,', a.repeats, 'x 5 folds')
    for name, r in (('v3.1', res_old), ('new', res_new)):
        s = score(r)
        print('  %-5s ' % name + '  '.join('%s=%.3f' % (k, v) for k, v in s.items() if isinstance(v, float)))


def _fmt(v):
    return '%.1f%%' % (100 * v) if isinstance(v, float) and not math.isnan(v) else 'n/a'


def cmd_evaluate(a):
    D = load_data(a.data)
    gold, train, test = load_gold(a.labels, a.split, D)
    V = Vectors(D)
    m = Model(V, sorted(train), gold)
    te = sorted(test)
    st = m.states(te)
    new = [(gold[i], s[0]) for i, s in zip(te, st)]
    old = [(gold[i], V31_STATE(D['pis'][i])) for i in te]
    os.makedirs(a.out, exist_ok=True)
    keys = ['coverage', 'accuracy_all', 'accuracy_when_placed', 'macro_f1', 'f1_W', 'f1_H', 'f1_D',
            'wet_precision', 'wet_recall', 'unclear_left_unclassified']
    so, sn = score(old), score(new)
    rows = []
    for k in keys:
        lo_o, hi_o = bootstrap(old, k)
        lo_n, hi_n = bootstrap(new, k)
        dl, dh = bootstrap_diff(new, old, k)
        rows.append((k, so[k], lo_o, hi_o, sn[k], lo_n, hi_n, dl, dh))
    with open(os.path.join(a.out, 'evaluation.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['metric', 'v3.1', 'v3.1_lo', 'v3.1_hi', 'new', 'new_lo', 'new_hi', 'diff_lo', 'diff_hi'])
        for r in rows:
            w.writerow([r[0]] + ['%.4f' % x for x in r[1:]])
    # confusion tables
    def conf(pairs):
        names = {None: 'unclassified', 'W': 'wet side', 'D': 'dry side', 'H': 'hybrid'}
        t = {}
        for g, s in pairs:
            t[(g, names[SIDE[s]])] = t.get((g, names[SIDE[s]]), 0) + 1
        cols = ['wet side', 'hybrid', 'dry side', 'unclassified']
        lines = ['| gold \\ predicted | ' + ' | '.join(cols) + ' |', '|' + '---|' * (len(cols) + 1)]
        for g in 'WHDU':
            lines.append('| %s | ' % {'W': 'wet', 'H': 'hybrid', 'D': 'dry', 'U': 'unclear'}[g] +
                         ' | '.join(str(t.get((g, c), 0)) for c in cols) + ' |')
        return '\n'.join(lines)
    with open(os.path.join(a.out, 'evaluation.md'), 'w') as f:
        f.write('# Wet/dry model: locked test set\n\n')
        f.write('%d investigators, drawn at random and labelled by reading their records before any '
                'model output was looked at. None of them was used to fit or tune the model.\n\n' % len(te))
        f.write('| metric | v3.1 (keyword score) | new model | difference (95% CI) |\n|---|---|---|---|\n')
        for r in rows:
            f.write('| %s | %s (%s-%s) | %s (%s-%s) | %+.1f to %+.1f pts |\n' % (
                r[0], _fmt(r[1]), _fmt(r[2]), _fmt(r[3]), _fmt(r[4]), _fmt(r[5]), _fmt(r[6]),
                100 * r[7], 100 * r[8]))
        f.write('\nScored on the %d test people whose gold label is wet, hybrid or dry; the %d the '
                'labeller could not call are only used for the last row.\n\n' % (sn['n_scored'], sn['n_unclear']))
        f.write('## v3.1\n\n' + conf(old) + '\n\n## New model\n\n' + conf(new) + '\n')
    with open(os.path.join(a.out, 'test_predictions.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['index', 'name', 'gold', 'v31_state', 'new_state', 'p_wet'])
        for i, s in zip(te, st):
            w.writerow([i, D['pis'][i]['n'], gold[i], V31_STATE(D['pis'][i]), s[0], '%.3f' % s[1]])
    print(open(os.path.join(a.out, 'evaluation.md')).read())


def readable(term):
    """A term worth showing a reader: no stop words, nothing trivially short."""
    ws = term.split()
    return all(len(w) >= 3 and w not in ENGLISH_STOP_WORDS for w in ws)


def top_terms(V, tm, k=25):
    names = np.array(V.tv.get_feature_names_out())
    co = tm.coef_[0]
    o = np.argsort(co)
    return ([t for t in names[o[::-1][:4 * k]] if readable(t)][:k],
            [t for t in names[o[:4 * k]] if readable(t)][:k])


def cmd_predict(a):
    """Fit on every gold label (train and test) and score all investigators."""
    D = load_data(a.data)
    gold, train, test = load_gold(a.labels, a.split, D)
    V = Vectors(D)
    m = Model(V, sorted(train | test), gold)
    everyone = list(range(len(D['pis'])))
    st = m.states(everyone)
    names = np.array(V.tv.get_feature_names_out())
    co = m.tm.coef_[0]
    out = []
    for i, (s, p, why) in zip(everyone, st):
        # the title that pushed hardest each way, as evidence a reader can check
        ev = {'model': MODEL_VERSION, 'P': round(p, 3), 'n_titles': len(V.by_person[i]),
              'n_grants': int(V.ngrant[i])}
        rows = V.by_person[i]
        if rows:
            pr = m.tm.predict_proba(V.Xt[rows])[:, 1]
            ev['title_mean'] = round(float(pr.mean()), 3)
            ev['wet_titles'] = int((pr > 0.5).sum())
            j = int(np.argmax(pr))
            raw = titles_of(D['pis'][i], raw=True)
            ev['most_wet'] = [raw[j][:140], round(float(pr[j]), 2)]
            j = int(np.argmin(pr))
            ev['most_dry'] = [raw[j][:140], round(float(pr[j]), 2)]
            row = V.Xt[rows].sum(axis=0).A1 * co
            o = np.argsort(row)
            # the words shown to a reader: content words only, and only the side
            # the call landed on (both sides for a hybrid)
            words = lambda seq, sign: [names[t] for t in seq if sign * row[t] > 0 and readable(names[t])][:3]
            if s in (1, 4, 3):
                ev['wet_terms'] = words(o[::-1][:40], 1)
            if s in (2, 5, 3):
                ev['dry_terms'] = words(o[:40], -1)
        if why:
            ev['why_unclassified'] = why
        out.append({'l': s, 'c': round(100 * p, 1), 'ev': ev})
    wet, dry = top_terms(V, m.tm)
    json.dump({'model': MODEL_VERSION, 'bands': m.bands,
               'trained_on': len([i for i in gold if gold[i] in 'WHD']),
               'top_wet_terms': wet, 'top_dry_terms': dry, 'people': out},
              open(a.out, 'w'), separators=(',', ':'))
    from collections import Counter
    print('states:', Counter(o['l'] for o in out))
    print('wet terms:', ', '.join(wet[:15]))
    print('dry terms:', ', '.join(dry[:15]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['cv', 'evaluate', 'predict'])
    ap.add_argument('--data', required=True)
    ap.add_argument('--split', required=True)
    ap.add_argument('--labels', required=True)
    ap.add_argument('--out', default='wetdry_out')
    ap.add_argument('--repeats', type=int, default=3)
    a = ap.parse_args()
    {'cv': cmd_cv, 'evaluate': cmd_evaluate, 'predict': cmd_predict}[a.cmd](a)


if __name__ == '__main__':
    main()
