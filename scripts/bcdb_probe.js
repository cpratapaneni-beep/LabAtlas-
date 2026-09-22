/* What is actually on the BCDB faculty page?
 *
 * Paste this into the console on the faculty directory. It changes nothing and
 * collects no names - it reports how the page is built, so the extractor can be
 * pointed at the real list instead of guessing. It downloads bcdb_probe.txt;
 * send that back.
 *
 * If the page has a Search button, press it first so the results are on screen.
 */
(() => {
const out = [];
const say = (...a) => { const s = a.join(' '); out.push(s); console.log(s); };

say('URL      ', location.href);
say('title    ', document.title);
say('body text', (document.body.innerText || '').length, 'chars');

/* ---- the shape of the page ---------------------------------------------- */
const counts = {};
document.querySelectorAll('*').forEach(n => { counts[n.tagName] = (counts[n.tagName] || 0) + 1; });
say('\nelements :', Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 12)
  .map(([t, n]) => `${t}=${n}`).join(' '));

/* ---- repeated classes: a list of people looks like a repeated class ------- */
const cls = {};
document.querySelectorAll('div,li,article,section,tr,span,a').forEach(n =>
  (n.className && typeof n.className === 'string' ? n.className.split(/\s+/) : [])
    .forEach(c => { if (c.length > 2) cls[c] = (cls[c] || 0) + 1; }));
const repeated = Object.entries(cls).filter(([, n]) => n >= 4).sort((a, b) => b[1] - a[1]).slice(0, 25);
say('\nrepeated classes (4+):');
repeated.forEach(([c, n]) => say('   ', String(n).padStart(4), c));

/* ---- anything that looks like a results container ------------------------ */
say('\ncontainers named like results or faculty:');
document.querySelectorAll('[class*=result],[id*=result],[class*=faculty],[id*=faculty],' +
  '[class*=people],[class*=person],[class*=member],[class*=directory],[class*=listing],[class*=profile]')
  .forEach(n => {
    const kids = n.children.length;
    const txt = (n.innerText || '').replace(/\s+/g, ' ').trim();
    if (kids === 0 && !txt) return;
    say('   ', (n.tagName + '.' + (typeof n.className === 'string' ? n.className : '')).slice(0, 70),
      '| children', kids, '| text', txt.length, '|', JSON.stringify(txt.slice(0, 90)));
  });

/* ---- links that look like a person's profile ----------------------------- */
const profile = [...document.querySelectorAll('a[href]')]
  .filter(a => /\/(bio|bios|faculty|people|person|profile|member)s?\//i.test(a.getAttribute('href') || ''))
  .map(a => ((a.innerText || '').replace(/\s+/g, ' ').trim() || '(no text)') + '  ->  ' + a.getAttribute('href'));
say('\nprofile-shaped links:', profile.length);
profile.slice(0, 25).forEach(l => say('   ', l.slice(0, 120)));

/* ---- forms: this page is a search, so what does it search? --------------- */
say('\nforms:', document.forms.length);
[...document.forms].forEach((f, i) => say('   form', i, f.getAttribute('action') || '(no action)',
  '| method', f.method, '| controls', f.elements.length));
say('buttons:', [...document.querySelectorAll('button,input[type=submit]')]
  .map(b => JSON.stringify(((b.innerText || b.value || '').trim()).slice(0, 30))).slice(0, 12).join(' '));

/* ---- where does its data come from? -------------------------------------- */
const src = document.documentElement.outerHTML;
const urls = new Set();
(src.match(/["'](\/[^"'\s]{4,140}|https?:\/\/[^"'\s]{6,180})["']/g) || []).forEach(m => {
  const u = m.slice(1, -1);
  if (/(\.json|\/api\/|\/ajax|\/rest\/|\/services\/|\/feed|\/search\?|\/query|graphql|solr)/i.test(u)) urls.add(u);
});
say('\ndata-ish URLs:', urls.size);
[...urls].slice(0, 15).forEach(u => say('   ', u));

/* ---- a sample of the page's own text, so the real names can be seen ------ */
const clone = document.body.cloneNode(true);
clone.querySelectorAll('nav,header,footer,aside,script,style,noscript,select,option,datalist,form')
  .forEach(n => n.remove());
clone.style.cssText = 'position:fixed;left:-9999px;top:0';
document.body.appendChild(clone);
const lines = (clone.innerText || '').split(/\r?\n/).map(s => s.trim()).filter(Boolean);
clone.remove();
say('\ntext lines after chrome and forms are removed:', lines.length);
say('first 60 of them:');
lines.slice(0, 60).forEach((l, i) => say('   ', String(i).padStart(3), JSON.stringify(l.slice(0, 96))));

const blob = new Blob([out.join('\n')], { type: 'text/plain' });
const a = document.createElement('a');
a.href = URL.createObjectURL(blob); a.download = 'bcdb_probe.txt'; a.click();
console.log('%cSaved bcdb_probe.txt - send that file back.', 'font-weight:bold');
})();
