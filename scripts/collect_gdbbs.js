/* Collect Emory's GDBBS faculty rosters from inside your own browser.
 * ---------------------------------------------------------------------------
 * Nothing outside your browser needs to be able to reach biomed.emory.edu for
 * this: the program directories are all on that one origin, so a snippet
 * running on any page of it may fetch every other page of it. No install, no
 * Python, no extension, no CORS.
 *
 * HOW TO USE IT
 *   1. Open https://biomed.emory.edu/about-us/faculty-search.html
 *   2. Open the browser console (F12, or Cmd-Option-J / Ctrl-Shift-J)
 *   3. Paste this whole file in and press Enter
 *   4. Run:   await GDBBS.all()
 *
 * It reads each program's faculty directory, prints what it found per program,
 * and downloads `gdbbs.json`. Load that file into the atlas: Notes -> Load a
 * GDBBS roster -> Choose a file (or just drop it on the page).
 *
 * IF A PROGRAM COMES BACK EMPTY
 * Its list is probably drawn by JavaScript after the page loads, so the HTML
 * that arrives is a shell. Open that program's directory yourself, scroll to
 * the bottom so every entry has rendered, then run:
 *
 *   GDBBS.here('MMG')        // whichever program you are looking at
 *
 * That reads the page you can see rather than the page as delivered. Results
 * accumulate across pages, so do that for each stubborn program and then:
 *
 *   GDBBS.save()
 *
 * OTHER COMMANDS
 *   GDBBS.show()             print what has been collected so far
 *   GDBBS.reset()            throw it away and start again
 *   GDBBS.roster             the object itself, if you want to inspect it
 */
(() => {
'use strict';

// the origin the directories live on: this one when the snippet is already
// running there, the canonical host otherwise, or whatever a caller sets
const BASE = window.GDBBS_BASE ||
  (/(^|\.)emory\.edu$/i.test(location.hostname) ? location.origin : 'https://biomed.emory.edu');

const PROGRAMS = {
  BCDB: 'Biochemistry, Cell and Developmental Biology',
  BME:  'Biomedical Engineering',
  BP:   'Biological and Biomedical Physics',
  CB:   'Cancer Biology',
  GMB:  'Genetics and Molecular Biology',
  IMP:  'Immunology and Molecular Pathogenesis',
  MMG:  'Microbiology and Molecular Genetics',
  MSP:  'Molecular and Systems Pharmacology',
  NS:   'Neuroscience',
  PBEE: 'Population Biology, Ecology and Evolution'
};
const urlsFor = code => [
  `${BASE}/PROGRAM_SITES/${code}/about-us/faculty-search.html`,
  `${BASE}/PROGRAM_SITES/${code}/guides/faculty.html`,
  `${BASE}/PROGRAM_SITES/${code}/about-us/faculty.html`
];
const ALL_FACULTY = `${BASE}/about-us/faculty-search.html`;
const STORE = 'gdbbs-collect';

/* ---- reading a directory -------------------------------------------------
   The same rules the atlas and the Python scraper use, so a name read here is
   a name they will recognise. */
const ACCEPT = /(accepting\s+(new\s+)?(graduate\s+|rotation\s+)?students|currently\s+accepting|taking\s+(new\s+)?students|open\s+to\s+rotation)/i;
const REFUSE = /(not\s+(currently\s+)?accepting|no\s+longer\s+accepting|closed\s+to\s+rotation)/i;
const ROLE = new RegExp('\\b(professor|prof|faculty|lecturer|instructor|director|chair|chairman|' +
  'chairwoman|dean|fellow|fellows|scientist|scholar|adjunct|affiliate|emeritus|emerita|associate|' +
  'assistant|program|programme|department|division|school|college|center|centre|institute|laboratory|' +
  'university|hospital|clinic|graduate|student|students|research|admissions|contact|search|menu|home|' +
  'news|events|overview|people|alumni|seminar|apply|giving|login|resources|accepting|rotation|' +
  'publications|profile|email|phone|website|more|back|next|previous)\\b', 'i');
const W = "[A-Z][A-Za-z'’\\-]{1,}";
const P = `(?:${W}|[A-Z]\\.?|van|von|der|den|ten|ter|de|del|della|da|di|dos|du|la|le|op|bin|ibn|al|abu|st|Mc|Mac)`;
const DEG = "(?:Ph\\.?\\s?D|M\\.?D|D\\.?V\\.?M|D\\.?D\\.?S|Sc\\.?D|M\\.?P\\.?H|M\\.?S|D\\.?Phil|M\\.?B\\.?B\\.?S|R\\.?N|Pharm\\.?D)";
const NAME = new RegExp(`^(${W}(?:\\s+${P}){1,4})(?:\\s*,?\\s*${DEG}[.\\w\\s,/&-]*)?$`);
const NAME_REV = new RegExp(`^(${W}(?:\\s+${P}){0,2})\\s*,\\s*(${W}(?:\\s+${P}){0,2})(?:\\s*,?\\s*${DEG}[.\\w\\s,/&-]*)?$`);
const JUNK = ['emory university', 'graduate division', 'faculty search', 'our faculty',
  'program sites', 'contact us', 'about us', 'quick links', 'read more', 'learn more',
  'apply now', 'privacy policy'];
// Site furniture reads as a name the moment it is title case: "Request Info",
// "Imposter Syndrome", "Meet Our Community". No surname is made of these words,
// so a candidate carrying one is not a person. This is the second line of
// defence; dropping navigation is the first, and that only works where a menu
// is actually marked up as one.
const NOTNAME = new RegExp('\\b(all|any|full|member|members|level|levels|select|choose|filter|' +
  'filters|sort|show|clear|reset|submit|about|admissions|alumni|announcements|application|apply|asked|' +
  'awards|bylaws|calendar|careers|committees|community|contact|curriculum|deadlines|directory|' +
  'donate|employment|events|faq|fellowships|financial|forms|frequently|funding|governance|' +
  'guidelines|handbook|highlights|history|home|hours|imposter|incoming|info|information|' +
  'interface|join|jobs|leadership|learn|links|mission|newsletter|opportunities|orientation|' +
  'overview|policies|policy|privacy|prospective|questions|read|request|requirements|resources|' +
  'retreat|seminar|spotlight|statement|stories|support|symposium|syndrome|testimonials|tools|' +
  'tour|training|values|vision|visit|web|welcome|workshop|our|your|the|this)\\b', 'i');
// a unit is not a person either
const FIELD = new RegExp('\\b(genetics|genomics|proteomics|biology|biochemistry|chemistry|' +
  'medicine|pediatrics|paediatrics|surgery|neurology|neuroscience|pathology|immunology|' +
  'microbiology|pharmacology|physiology|psychiatry|psychology|radiology|oncology|epidemiology|' +
  'biostatistics|informatics|engineering|nursing|ophthalmology|dermatology|anesthesiology|' +
  'urology|orthopaedics|orthopedics|cardiology|physics|mathematics|statistics|sociology|' +
  'anthropology|economics|ecology|evolution|endocrinology|rheumatology|nephrology|hematology|' +
  'gastroenterology|obstetrics|gynecology|otolaryngology|radiation)\\b', 'i');

function lineName(line) {
  line = String(line || '').replace(/^[\s|*\-#>\u2022\u00b7]+|[\s|*\-#>\u2022\u00b7]+$/g, '');
  if (line.length < 4 || line.length > 70) return null;
  const low = line.toLowerCase();
  if (JUNK.some(j => low.includes(j)) || ROLE.test(line) || FIELD.test(line)) return null;
  if (/\d/.test(line) || line.includes('@') || low.includes('http')) return null;
  // a generational suffix is not part of the name, and the atlas strips it too
  line = line.replace(/[,\s]+(?:Jr|Sr|II|III|IV|V)\.?$/i, '').trim();
  // the plain form first: "Adam Gracz, PhD" is a name with a degree, not a flip
  let name = null;
  const m = NAME.exec(line);
  if (m) name = m[1];
  else { const rev = NAME_REV.exec(line); if (rev) name = rev[2] + ' ' + rev[1]; }
  if (!name) return null;
  const parts = name.replace(/\s+/g, ' ').trim().split(' ');
  if (parts.length < 2 || parts[0].replace(/\.$/, '').length < 2 ||
      parts[parts.length - 1].replace(/\.$/, '').length < 2) return null;
  name = parts.join(' ');
  // judged on what came out, after any degree has gone
  if (NOTNAME.test(name)) return null;
  // an acronym is a unit or a programme, never a person; a lone capital is an initial
  if (parts.some(function (w) { const t = w.replace(/[.,]/g, ''); return t.length > 1 && t === t.toUpperCase(); }))
    return null;
  return name;
}

function readText(text) {
  const lines = String(text || '').split(/\r?\n/).map(s => s.replace(/[\t ]+/g, ' ').trim());
  const says = ACCEPT.test(text) || REFUSE.test(text);
  const out = new Map();
  for (let i = 0; i < lines.length; i++) {
    const name = lineName(lines[i]);
    if (!name) continue;
    let flag = null;
    if (says) {
      const block = [];
      for (let j = i + 1; j < Math.min(i + 9, lines.length); j++) {
        if (lineName(lines[j])) break;
        block.push(lines[j]);
      }
      const around = block.join(' ');
      if (REFUSE.test(around)) flag = false;
      else if (ACCEPT.test(around)) flag = true;
    }
    if (!out.has(name) || (out.get(name) === null && flag !== null)) out.set(name, flag);
  }
  return out;
}

/* A directory that renders its list from an embedded payload hides every name
   in a <script>. Worth a look before giving up on a page. */
function readEmbedded(doc) {
  const out = new Map();
  doc.querySelectorAll('script').forEach(s => {
    const src = s.textContent || '';
    if (src.length < 40 || !/name|title|faculty/i.test(src)) return;
    const hits = src.match(/"(?:name|fullName|full_name|displayName|title)"\s*:\s*"([^"]{4,70})"/g) || [];
    hits.forEach(h => {
      const v = h.replace(/^[^:]*:\s*"/, '').replace(/"$/, '');
      const n = lineName(v);
      if (n && !out.has(n)) out.set(n, null);
    });
  });
  return out;
}

/* A document from DOMParser is parsed but never laid out, so it has no
   innerText at all and its textContent runs every element together on one
   line. The text is rebuilt here instead, one line per block, which is what
   the name reader above expects to be given. */
const BLOCK = /^(P|DIV|LI|TR|TD|TH|BR|H1|H2|H3|H4|H5|H6|SECTION|ARTICLE|HEADER|FOOTER|NAV|UL|OL|DL|DT|DD|TABLE|FIGURE|FIGCAPTION|BLOCKQUOTE|ASIDE|MAIN|FORM|HR)$/;
function domText(node, out) {
  out = out || [];
  node.childNodes.forEach(n => {
    if (n.nodeType === 3) { out.push(n.nodeValue); return; }
    if (n.nodeType !== 1) return;
    const tag = n.tagName;
    if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') return;
    const block = BLOCK.test(tag);
    if (block) out.push('\n');
    domText(n, out);
    if (block) out.push('\n');
  });
  return out;
}

function readDoc(doc) {
  const embedded = readEmbedded(doc);
  doc.querySelectorAll('script,style,noscript').forEach(n => n.remove());
  const text = domText(doc.body || doc).join('').replace(/[ \t\u00a0]+/g, ' ');
  const found = readText(text);
  embedded.forEach((v, k) => { if (!found.has(k)) found.set(k, v); });
  return found;
}
function readHTML(html) {
  return readDoc(new DOMParser().parseFromString(html, 'text/html'));
}

/* ---- the roster ---------------------------------------------------------- */
function blank() {
  return {
    generated: new Date().toISOString().slice(0, 10),
    source: BASE,
    programs: { ...PROGRAMS },
    people: {}
  };
}
function load() {
  try { const r = localStorage.getItem(STORE); if (r) return JSON.parse(r); } catch (e) {}
  return blank();
}
function keep(r) { try { localStorage.setItem(STORE, JSON.stringify(r)); } catch (e) {} }

const API = { roster: load() };

function merge(code, found, url) {
  let added = 0, accepting = 0;
  found.forEach((flag, name) => {
    const rec = API.roster.people[name] || (API.roster.people[name] = { p: [], a: false, u: url });
    if (code && !rec.p.includes(code)) rec.p.push(code);
    if (flag === true) { rec.a = true; accepting++; }
    added++;
  });
  keep(API.roster);
  return { added, accepting };
}

API.here = function (code) {
  code = String(code || '').toUpperCase();
  if (code && !PROGRAMS[code]) console.warn(`"${code}" is not a GDBBS program code; storing the names anyway`);
  // the live page, with its chrome taken out the way a fetched one's is
  const clone = document.body.cloneNode(true);
  clone.querySelectorAll('nav,header,footer,aside,script,style,noscript,select,option,datalist,'
    + 'optgroup,label,legend,fieldset,form,[role=navigation],[role=search],[class*=nav],[class*=menu],'
    + '[class*=breadcrumb],[class*=sidebar],[class*=footer],[class*=header],[class*=filter],'
    + '[class*=facet],[class*=refine],[id*=nav],[id*=menu],[id*=filter]')
    .forEach(function (n) { n.remove(); });
  document.body.appendChild(clone);            // innerText needs a laid-out node
  clone.style.cssText = 'position:fixed;left:-9999px;top:0';
  const found = readText(clone.innerText || clone.textContent || '');
  clone.remove();
  const r = merge(code, found, location.href);
  console.log(`%c${code || 'GDBBS'}%c  ${found.size} names on this page, ${r.accepting} accepting  ` +
    `(${Object.keys(API.roster.people).length} collected so far)`,
    'font-weight:bold', 'font-weight:normal');
  return found.size;
};

API.page = async function (code, url) {
  try {
    const res = await fetch(url, { credentials: 'same-origin' });
    if (!res.ok) return { n: 0, why: `HTTP ${res.status}` };
    const found = readHTML(await res.text());
    if (!found.size) return { n: 0, why: 'no names in the delivered HTML' };
    const r = merge(code, found, url);
    return { n: found.size, accepting: r.accepting, url };
  } catch (e) {
    return { n: 0, why: `${e.name}: ${e.message}` };
  }
};

/* Same origin, so a page that builds its list in JavaScript can simply be
   rendered in a hidden frame and read once it has settled. This is what makes
   all() work end to end on a directory that ships an empty shell. */
API.frame = function (code, url, settle) {
  return new Promise(resolve => {
    const f = document.createElement('iframe');
    f.style.cssText = 'position:fixed;left:-9999px;top:0;width:1200px;height:2400px;opacity:0';
    let done = false;
    const finish = r => { if (done) return; done = true; f.remove(); resolve(r); };
    const timer = setTimeout(() => finish({ n: 0, why: 'the frame never loaded' }), 25000);
    f.onload = () => setTimeout(() => {
      clearTimeout(timer);
      let doc = null;
      try { doc = f.contentDocument; } catch (e) { /* framing refused */ }
      if (!doc || !doc.body) return finish({ n: 0, why: 'the page refused to be framed' });
      const found = readDoc(doc);
      if (!found.size) return finish({ n: 0, why: 'rendered, but no names in it' });
      const r = merge(code, found, url);
      finish({ n: found.size, accepting: r.accepting, url, framed: true });
    }, settle || 2500);
    f.onerror = () => { clearTimeout(timer); finish({ n: 0, why: 'the frame failed' }); };
    f.src = url;
    document.body.appendChild(f);
  });
};

API.all = async function () {
  console.log('Reading the GDBBS program directories\u2026\n');
  const empty = [];
  for (const code of Object.keys(PROGRAMS)) {
    let got = { n: 0, why: 'no page found' }, reached = null;
    for (const url of urlsFor(code)) {
      got = await API.page(code, url);
      if (got.n) break;
      if (got.why !== 'HTTP 404') reached = url;   // the page exists, it was just empty
    }
    // A page that came back without names is worth rendering before giving up.
    // So is one whose names came out of an embedded payload with no
    // accepting-students wording attached: rendering it recovers the flags,
    // and merging the two passes is additive.
    if (reached && (!got.n || !got.accepting)) {
      const framed = await API.frame(code, reached);
      if (framed.n && (!got.n || framed.accepting)) got = framed;
    }
    if (got.n) {
      console.log(`  ${code.padEnd(5)} ${String(got.n).padStart(4)} names, ${got.accepting} accepting` +
        `${got.framed ? ' (rendered)' : ''}   ${got.url}`);
    } else {
      empty.push(code);
      console.log(`  ${code.padEnd(5)}    0            ${got.why}`);
    }
  }
  let div = await API.page('', ALL_FACULTY);
  if (!div.n) div = await API.frame('', ALL_FACULTY);
  console.log(`  ALL   ${String(div.n).padStart(4)} names from the division-wide roster` +
    (div.n ? '' : `   ${div.why}`));

  const total = Object.keys(API.roster.people).length;
  const acc = Object.values(API.roster.people).filter(p => p.a).length;
  console.log(`\n${total} people, ${acc} listed as accepting students.`);
  if (empty.length) {
    console.log(`\n%cThese came back empty: ${empty.join(', ')}`, 'color:#c66');
    console.log('Open each one yourself, scroll to the bottom so every entry has rendered, and run  ' +
      "GDBBS.here('CODE')  on it. Then GDBBS.save().");
  }
  if (total) API.save();
  return API.roster;
};

API.save = function () {
  const blob = new Blob([JSON.stringify(API.roster, null, 1)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'gdbbs.json';
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  console.log(`Saved gdbbs.json — ${Object.keys(API.roster.people).length} people. ` +
    'Load it into the atlas: Notes → Load a GDBBS roster.');
};

API.show = function () {
  const rows = Object.entries(API.roster.people)
    .map(([name, r]) => ({ name, programs: (r.p || []).join(' '), accepting: !!r.a }));
  console.table(rows);
  return rows.length;
};

API.reset = function () {
  API.roster = blank();
  keep(API.roster);
  console.log('Cleared.');
};

API._read = readText;       // exposed so the parser can be tested on its own
API._readHTML = readHTML;

window.GDBBS = API;
const have = Object.keys(API.roster.people).length;
console.log('%cGDBBS collector ready.%c  Run:  await GDBBS.all()' +
  (have ? `\n${have} people already collected in this browser — GDBBS.reset() to start over.` : ''),
  'font-weight:bold', 'font-weight:normal');
})();
