/* Emory GDBBS faculty, read from a program's own faculty page.
 *
 * Open any program's faculty listing, e.g.
 *   https://biomed.emory.edu/PROGRAM_SITES/BCDB/about-us/faculty-search.html
 * paste this whole file into the console (F12) and press Enter.
 *
 * It reads the Faculty Listing table, and it does not guess: each entry gives a
 * name, an Emory email, and one line per GDBBS programme the person belongs to,
 * saying whether that membership is full, affiliate or adjunct. Because every
 * entry lists all of its memberships, one page already carries programme data
 * for everybody on it. Run it on each programme page to cover the division.
 *
 * It sets the table to show every row first, so nothing is left on page two.
 * Results accumulate across pages; it downloads gdbbs.json each time.
 *
 * A note on what "full" means, from this page's own wording: the three types of
 * membership are Full, Affiliate and Adjunct, and Full Graduate Faculty are the
 * ones with the right to act as dissertation advisors. That is the closest
 * thing the page states to "takes graduate students" - it is not a statement
 * that somebody is recruiting this year, and it is not recorded as one.
 */
(async () => {
const STORE = 'gdbbs-collect';
const PROGRAMS = {
  'BIOCHEMISTRY, CELL AND DEVELOPMENTAL BIOLOGY': 'BCDB',
  'BIOMEDICAL ENGINEERING': 'BME',
  'BIOLOGICAL AND BIOMEDICAL PHYSICS': 'BP',
  'CANCER BIOLOGY': 'CB',
  'GENETICS AND MOLECULAR BIOLOGY': 'GMB',
  'IMMUNOLOGY AND MOLECULAR PATHOGENESIS': 'IMP',
  'MICROBIOLOGY AND MOLECULAR GENETICS': 'MMG',
  'MOLECULAR AND SYSTEMS PHARMACOLOGY': 'MSP',
  'NEUROSCIENCE': 'NS',
  'POPULATION BIOLOGY, ECOLOGY AND EVOLUTION': 'PBEE',
  'POPULATION BIOLOGY, ECOLOGY, AND EVOLUTION': 'PBEE'
};
const NAMES = { BCDB: 'Biochemistry, Cell and Developmental Biology', BME: 'Biomedical Engineering',
  BP: 'Biological and Biomedical Physics', CB: 'Cancer Biology', GMB: 'Genetics and Molecular Biology',
  IMP: 'Immunology and Molecular Pathogenesis', MMG: 'Microbiology and Molecular Genetics',
  MSP: 'Molecular and Systems Pharmacology', NS: 'Neuroscience',
  PBEE: 'Population Biology, Ecology and Evolution' };

const DEGREE = /^(PHD|MD|DVM|DDS|SCD|MPH|MS|MSC|MBBS|PHARMD|RN|DPHIL|DO|MBA|JD|MA|BS|BA|MSN|DNP|DRPH|MSPH|FAAN|FACS|FAHA|FACC|MBA)$/;
// upper-case words that are page furniture rather than somebody's name
const NOTNAME = /\b(FACULTY|MEMBERSHIP|MEMBER|LISTING|SEARCH|RESET|FORM|MENU|SHOW|ENTRIES|PREVIOUS|NEXT|EMORY|GDBBS|PROGRAM|GRADUATE|ADJUNCT|AFFILIATE|FULL|PROFILE|WEBSITE|LAB|DEPARTMENT|SCHOOL|UNIVERSITY|CONTACT|ABOUT|HOME|APPLY|RESOURCES|STUDENTS|ALUMNI|NEWS|EVENTS)\b/;

/* "FIKRI AVCI, PHD (HE/HIM)" -> "Fikri Avci".  The listing is upper case
   throughout, so case cannot be used to find a name - the shape has to. */
function readName(line) {
  let s = String(line || '').trim();
  if (!s || s.length > 90 || s.includes('@') || /\d/.test(s)) return null;
  if (/\bMEMBER\s*[-–]/.test(s)) return null;      // a membership line
  s = s.replace(/\([^)]*\)/g, '').trim();               // drop pronouns
  const parts = s.split(',').map(x => x.trim()).filter(Boolean);
  if (!parts.length) return null;
  // everything after the first comma has to be a degree, or this is prose
  for (const extra of parts.slice(1)) {
    if (!DEGREE.test(extra.replace(/[.\s]/g, '').toUpperCase())) return null;
  }
  const base = parts[0];
  if (base !== base.toUpperCase()) return null;         // the listing is upper case
  if (NOTNAME.test(base)) return null;
  const words = base.split(/\s+/).filter(Boolean);
  if (words.length < 2 || words.length > 5) return null;
  if (!words.every(w => /^[A-Z][A-Z'’.\-]*$/.test(w))) return null;
  if (words[0].replace(/\./g, '').length < 2) return null;
  const title = base.toLowerCase().replace(/(^|[\s'’\-])([a-z])/g, (m, a, b) => a + b.toUpperCase());
  return title.replace(/\b([A-Za-z])\b/g, (m, c) => c.toUpperCase() + '.').replace(/\.\./g, '.');
}

/* show every row before reading, so nobody is left on page two */
function showAll() {
  const sel = document.querySelector('select[name$="_length"], .dataTables_length select');
  if (!sel) return 0;
  const best = [...sel.options].map(o => parseInt(o.value, 10))
    .filter(n => !isNaN(n)).sort((a, b) => b - a)[0];
  if (!best || String(best) === sel.value) return 0;
  sel.value = String(best);
  sel.dispatchEvent(new Event('change', { bubbles: true }));
  return best;
}
const bumped = showAll();
if (bumped) { console.log(`Set the table to show ${bumped} rows; waiting for it to redraw…`);
  await new Promise(r => setTimeout(r, 1200)); }

const table = document.querySelector('table.dataTable, .dataTables_wrapper table, table');
if (!table) { console.log('%cNo faculty table on this page.', 'color:#c66'); return; }
const lines = (table.innerText || '').split(/\r?\n/).map(s => s.replace(/\s+/g, ' ').trim());

const here = {};
let cur = null;
for (const line of lines) {
  const mem = /^(FULL|AFFILIATE|ADJUNCT)\s+MEMBER\s*[-–]\s*(.+)$/i.exec(line);
  if (mem && cur) {
    const code = PROGRAMS[mem[2].trim().toUpperCase()];
    if (code) {
      if (!cur.p.includes(code)) cur.p.push(code);
      cur.m[code] = mem[1].toLowerCase();
    } else {
      cur.unknown = (cur.unknown || []).concat(mem[2].trim());
    }
    continue;
  }
  const mail = /([\w.\-+]+@[\w.\-]*emory\.edu)/i.exec(line);
  if (mail && cur && !cur.em) { cur.em = mail[1].toLowerCase(); continue; }
  const name = readName(line);
  if (name) { cur = here[name] = here[name] || { p: [], m: {}, a: false, u: location.href }; }
}

// merge into whatever earlier pages left in this browser
let roster;
try { roster = JSON.parse(localStorage.getItem(STORE)); } catch (e) { roster = null; }
if (!roster || !roster.people) roster = { generated: '', source: location.origin, programs: {}, people: {} };
roster.generated = new Date().toISOString().slice(0, 10);
let fresh = 0;
for (const [name, rec] of Object.entries(here)) {
  const was = roster.people[name];
  if (!was) { roster.people[name] = rec; fresh++; continue; }
  rec.p.forEach(c => { if (!was.p.includes(c)) was.p.push(c); });
  Object.assign(was.m = was.m || {}, rec.m);
  if (rec.em && !was.em) was.em = rec.em;
}
Object.keys(roster.people).forEach(n => (roster.people[n].p || []).forEach(c => { roster.programs[c] = NAMES[c] || c; }));
try { localStorage.setItem(STORE, JSON.stringify(roster)); } catch (e) {}

const found = Object.keys(here).length;
const total = Object.keys(roster.people).length;
const full = Object.values(roster.people).filter(r => Object.values(r.m || {}).includes('full')).length;
const mailed = Object.values(roster.people).filter(r => r.em).length;
console.log(`%c${found} on this page%c  ·  ${fresh} new  ·  ${total} collected so far  ·  ` +
  `${full} hold a full membership somewhere  ·  ${mailed} with an email`,
  'font-weight:bold', 'font-weight:normal');
console.table(Object.entries(here).map(([n, r]) => ({
  name: n, email: r.em || '', programs: r.p.join(' '),
  membership: r.p.map(c => c + ':' + (r.m[c] || '?')).join(' ')
})));
const info = document.querySelector('.dataTables_info');
if (info) console.log('table said:', info.innerText.trim());
const unknown = [...new Set(Object.values(here).flatMap(r => r.unknown || []))];
if (unknown.length) console.log('%cUnrecognised programme names: ' + unknown.join(' | '), 'color:#c66');

if (!found) {
  console.log('%cNothing read. Is the Faculty Listing table on screen?', 'color:#c66');
} else {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(roster, null, 1)], { type: 'application/json' }));
  a.download = 'gdbbs.json'; a.click();
  console.log('Saved gdbbs.json. Repeat on the other programme pages, then load it in the atlas: ' +
    'Notes → Load a GDBBS roster.   (GDBBS_RESET() to start over.)');
}
window.GDBBS_RESET = () => { localStorage.removeItem(STORE); console.log('Cleared.'); };
})();
