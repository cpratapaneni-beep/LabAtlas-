/* BCDB faculty, straight from the browser console.
 * Open https://biomed.emory.edu/PROGRAM_SITES/BCDB/about-us/faculty-search.html
 * then paste this whole block and press Enter. It reads the page you are
 * looking at - already rendered, so a JavaScript-built list is fine - and
 * downloads gdbbs.json. Load that in the atlas: Notes -> Load a GDBBS roster.
 *
 * Another program: change CODE below, open that program's page, paste again.
 * (Chrome may ask you to type  allow pasting  in the console first.)
 */
(() => {
const CODE = 'BCDB';
const A = /(accepting\s+(new\s+)?(graduate\s+|rotation\s+)?students|currently\s+accepting|taking\s+(new\s+)?students)/i;
const R = /(not\s+(currently\s+)?accepting|no\s+longer\s+accepting)/i;
const ROLE = /\b(professor|prof|faculty|lecturer|instructor|director|chair|dean|fellow|scientist|scholar|adjunct|affiliate|emeritus|emerita|associate|assistant|program|department|division|school|college|center|centre|institute|laboratory|university|hospital|clinic|graduate|students?|research|admissions|contact|search|menu|home|news|events|overview|people|alumni|seminar|apply|giving|login|resources|accepting|rotation|publications|profile|email|phone|website|more|back|next|previous)\b/i;
const NOT = /\b(all|any|full|member|members|level|levels|select|choose|filter|filters|sort|show|clear|reset|submit|about|admissions|alumni|application|apply|asked|awards|calendar|careers|community|contact|curriculum|deadlines|directory|donate|events|faq|financial|forms|frequently|funding|handbook|history|home|hours|imposter|info|information|interface|join|jobs|leadership|learn|links|mission|newsletter|orientation|overview|policies|policy|privacy|questions|read|request|requirements|resources|retreat|seminar|statement|stories|support|symposium|syndrome|tools|tour|training|values|vision|visit|web|welcome|workshop|our|your|the|this)\b/i;
const FIELD = /\b(genetics|genomics|biology|biochemistry|chemistry|medicine|pediatrics|surgery|neurology|neuroscience|pathology|immunology|microbiology|pharmacology|physiology|psychiatry|psychology|radiology|oncology|epidemiology|biostatistics|informatics|engineering|nursing|ophthalmology|dermatology|cardiology|physics|statistics|ecology|evolution)\b/i;
const W = "[A-Z][A-Za-z'’\\-]{1,}";
const P = `(?:${W}|[A-Z]\\.?|van|von|der|den|de|del|della|da|di|dos|du|la|le|Mc|Mac)`;
const D = "(?:Ph\\.?\\s?D|M\\.?D|D\\.?V\\.?M|D\\.?D\\.?S|Sc\\.?D|M\\.?P\\.?H|M\\.?S|M\\.?B\\.?B\\.?S|Pharm\\.?D|R\\.?N)";
const NAME = new RegExp(`^(${W}(?:\\s+${P}){1,4})(?:\\s*,?\\s*${D}[.\\w\\s,/&-]*)?$`);
const REV = new RegExp(`^(${W}(?:\\s+${P}){0,2})\\s*,\\s*(${W}(?:\\s+${P}){0,2})(?:\\s*,?\\s*${D}[.\\w\\s,/&-]*)?$`);

function nameOf(s) {
  s = String(s || '').replace(/^[\s|*\-#>•·]+|[\s|*\-#>•·]+$/g, '');
  if (s.length < 4 || s.length > 70) return null;
  if (ROLE.test(s) || FIELD.test(s) || /\d/.test(s) || s.includes('@')) return null;
  s = s.replace(/[,\s]+(?:Jr|Sr|II|III|IV|V)\.?$/i, '').trim();
  let n = null, m = NAME.exec(s);
  if (m) n = m[1]; else { const r = REV.exec(s); if (r) n = r[2] + ' ' + r[1]; }
  if (!n) return null;
  const w = n.replace(/\s+/g, ' ').trim().split(' ');
  if (w.length < 2 || w[0].replace(/\.$/, '').length < 2 || w[w.length - 1].replace(/\.$/, '').length < 2) return null;
  n = w.join(' ');
  if (NOT.test(n)) return null;
  if (w.some(x => { const t = x.replace(/[.,]/g, ''); return t.length > 1 && t === t.toUpperCase(); })) return null;
  return n;
}

/* the page without its chrome, so menu items are never read as people */
const body = document.body.cloneNode(true);
/* chrome, and the search form: a filter menu's options are research topics */
/* and membership levels, and every one of them reads as a name in title case */
body.querySelectorAll('nav,header,footer,aside,script,style,noscript,select,option,datalist,\
optgroup,label,legend,fieldset,form,[role=navigation],[role=search],[class*=nav],[class*=menu],\
[class*=breadcrumb],[class*=sidebar],[class*=footer],[class*=header],[class*=filter],[class*=facet],\
[class*=refine],[id*=nav],[id*=menu],[id*=filter]').forEach(n => n.remove());
body.style.cssText = 'position:fixed;left:-9999px;top:0';
document.body.appendChild(body);
const text = body.innerText || body.textContent || '';
body.remove();

const lines = text.split(/\r?\n/).map(s => s.trim());
const says = A.test(text) || R.test(text);
const people = {};
for (let i = 0; i < lines.length; i++) {
  const n = nameOf(lines[i]);
  if (!n) continue;
  let flag = null;
  if (says) {
    const blk = [];
    for (let j = i + 1; j < Math.min(i + 9, lines.length); j++) { if (nameOf(lines[j])) break; blk.push(lines[j]); }
    const s = blk.join(' ');
    flag = R.test(s) ? false : A.test(s) ? true : null;
  }
  if (!(n in people) || (people[n].a === false && flag === true)) people[n] = { p: [CODE], a: flag === true, u: location.href };
}

const names = Object.keys(people);
console.log(`%c${CODE}%c  ${names.length} names, ${names.filter(n => people[n].a).length} accepting students`,
  'font-weight:bold', 'font-weight:normal');
console.table(names.sort().map(n => ({ name: n, accepting: people[n].a })));
/* A person's name usually carries an initial, a particle or a third part. A */
/* page of research topics - "Brain Tumors", "Wound Healing" - carries none, and */
/* no word list can tell those from surnames, so this is said rather than acted on. */
const personish = names.filter(n => /\b[A-Z]\.?\b/.test(n) || n.includes("'") || n.split(' ').length > 2).length;
if (names.length > 5 && personish === 0)
  console.log('%cNone of these look like people: no initials, no particles, nothing but pairs of ' +
    'capitalised words. That is what a filter menu of research topics looks like. Check the table ' +
    'above before loading it.', 'color:#c66');
if (!names.length) {
  console.log('%cNothing found. Scroll to the bottom so every entry has rendered, then paste again.', 'color:#c66');
} else {
  const roster = { generated: new Date().toISOString().slice(0, 10), source: location.href,
                   programs: { [CODE]: 'Biochemistry, Cell and Developmental Biology' }, people };
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(roster, null, 1)], { type: 'application/json' }));
  a.download = 'gdbbs.json'; a.click();
  console.log('Saved gdbbs.json — load it in the atlas: Notes → Load a GDBBS roster.');
}
})();
