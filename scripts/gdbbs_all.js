/* Every Emory GDBBS programme, in one paste.
 *
 * Open any page on biomed.emory.edu - the BCDB faculty listing will do -
 * then paste this whole file into the console (F12) and press Enter.
 *
 * Every programme's faculty page sits on that one origin, so this fetches all
 * ten of them from where you already are. No CORS, no extension, nothing to
 * install. Each entry gives a name, an Emory email, and one line per programme
 * the person belongs to saying whether that membership is full, affiliate or
 * adjunct. It merges them, reports per programme, and downloads one gdbbs.json.
 *
 * A page whose table is not in the delivered HTML is rendered in a hidden frame
 * and read from there instead, which is the same origin too.
 *
 * On what "full" means, in the site's own words: the three memberships are
 * Full, Affiliate and Adjunct, and Full Graduate Faculty are the ones who may
 * act as dissertation advisors. That is not a statement that somebody is
 * recruiting this year, and it is not recorded as one.
 *
 * Block comments only and no returns at the top level, so this still runs if
 * the paste arrives flattened onto a single line.
 */
(async function () {
  var BASE = window.GDBBS_BASE ||
    ((/(^|\.)emory\.edu$/i.test(location.hostname)) ? location.origin : 'https://biomed.emory.edu');
  var PROGRAMS = {
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
  var NAMES = {
    BCDB: 'Biochemistry, Cell and Developmental Biology', BME: 'Biomedical Engineering',
    BP: 'Biological and Biomedical Physics', CB: 'Cancer Biology',
    GMB: 'Genetics and Molecular Biology', IMP: 'Immunology and Molecular Pathogenesis',
    MMG: 'Microbiology and Molecular Genetics', MSP: 'Molecular and Systems Pharmacology',
    NS: 'Neuroscience', PBEE: 'Population Biology, Ecology and Evolution'
  };
  var CODES = ['BCDB', 'BME', 'BP', 'CB', 'GMB', 'IMP', 'MMG', 'MSP', 'NS', 'PBEE'];
  var DEGREE = /^(PHD|MD|DVM|DDS|SCD|MPH|MS|MSC|MBBS|PHARMD|RN|DPHIL|DO|MBA|JD|MA|BS|BA|MSN|DNP|DRPH|MSPH|FAAN|FACS|FAHA|FACC)$/;
  var NOTNAME = /\b(FACULTY|MEMBERSHIP|MEMBER|LISTING|SEARCH|RESET|FORM|MENU|SHOW|ENTRIES|PREVIOUS|NEXT|EMORY|GDBBS|PROGRAM|GRADUATE|ADJUNCT|AFFILIATE|FULL|PROFILE|WEBSITE|LAB|DEPARTMENT|SCHOOL|UNIVERSITY|CONTACT|ABOUT|HOME|APPLY|RESOURCES|STUDENTS|ALUMNI|NEWS|EVENTS)\b/;

  function readName(line) {
    var s = String(line || '').trim();
    if (!s || s.length > 90 || s.indexOf('@') >= 0 || /\d/.test(s)) return null;
    if (/\bMEMBER\s*[-–]/.test(s)) return null;
    s = s.replace(/\([^)]*\)/g, '').trim();
    var parts = s.split(',').map(function (x) { return x.trim(); }).filter(Boolean);
    if (!parts.length) return null;
    for (var i = 1; i < parts.length; i++) {
      if (!DEGREE.test(parts[i].replace(/[.\s]/g, '').toUpperCase())) return null;
    }
    var base = parts[0];
    if (base !== base.toUpperCase()) return null;
    if (NOTNAME.test(base)) return null;
    var words = base.split(/\s+/).filter(Boolean);
    if (words.length < 2 || words.length > 5) return null;
    if (!words.every(function (w) { return /^[A-Z][A-Z'’.\-]*$/.test(w); })) return null;
    if (words[0].replace(/\./g, '').length < 2) return null;
    var title = base.toLowerCase().replace(/(^|[\s'’\-])([a-z])/g,
      function (m, a, b) { return a + b.toUpperCase(); });
    title = title.replace(/(^|\s)([A-Za-z])(?=\s|$)/g,
      function (m, a, c) { return a + c.toUpperCase() + '.'; });
    title = title.replace(/\bMc([a-z])/g, function (m, c) { return 'Mc' + c.toUpperCase(); });
    title = title.replace(/\b(Van|Von|Der|Den|Del|Della|De|Da|Di|Dos|Du|La|Le|Ter|Ten)\b(?!\.)/g,
      function (m, w, off) { return off === 0 ? m : m.toLowerCase(); });
    return title.replace(/\.\./g, '.');
  }

  /* A document from DOMParser is parsed but never laid out, so it has no
     innerText and its textContent runs every element onto one line. The text is
     rebuilt here, one line per block, which is what the reader above expects. */
  var BLOCK = /^(P|DIV|LI|TR|TD|TH|BR|H1|H2|H3|H4|H5|H6|SECTION|ARTICLE|UL|OL|DL|DT|DD|TABLE|TBODY|THEAD|FIGURE|BLOCKQUOTE|MAIN|FORM|HR)$/;
  function domText(node, out) {
    out = out || [];
    for (var i = 0; i < node.childNodes.length; i++) {
      var k = node.childNodes[i];
      if (k.nodeType === 3) { out.push(k.nodeValue); continue; }
      if (k.nodeType !== 1) continue;
      if (k.tagName === 'SCRIPT' || k.tagName === 'STYLE' || k.tagName === 'NOSCRIPT') continue;
      var block = BLOCK.test(k.tagName);
      if (block) out.push('\n');
      domText(k, out);
      if (block) out.push('\n');
    }
    return out;
  }

  function parseLines(lines) {
    var here = {}, cur = null;
    lines.forEach(function (line) {
      var mem = /^(FULL|AFFILIATE|ADJUNCT)\s+MEMBER\s*[-–]\s*(.+)$/i.exec(line);
      if (mem && cur) {
        var code = PROGRAMS[mem[2].trim().toUpperCase()];
        if (code) {
          if (cur.p.indexOf(code) < 0) cur.p.push(code);
          cur.m[code] = mem[1].toLowerCase();
        } else if (cur.unknown.indexOf(mem[2].trim()) < 0) {
          cur.unknown.push(mem[2].trim());
        }
        return;
      }
      var mail = /([\w.\-+]+@[\w.\-]*emory\.edu)/i.exec(line);
      if (mail && cur && !cur.em) { cur.em = mail[1].toLowerCase(); return; }
      var name = readName(line);
      if (name) {
        if (!here[name]) here[name] = { p: [], m: {}, a: false, unknown: [], u: '' };
        cur = here[name];
      }
    });
    return here;
  }

  function fromDoc(doc) {
    var table = doc.querySelector('table.dataTable, .dataTables_wrapper table, table');
    if (!table) return { here: {}, said: 0 };
    var text = domText(table).join('').replace(/[ \t ]+/g, ' ');
    var lines = text.split(/\r?\n/).map(function (s) { return s.trim(); });
    var info = doc.querySelector('.dataTables_info');
    var said = 0;
    if (info) {
      var mm = /of\s+([\d,]+)\s+entries/i.exec(info.textContent || '');
      if (mm) said = parseInt(mm[1].replace(/,/g, ''), 10);
    }
    return { here: parseLines(lines), said: said };
  }

  function fromLive(doc) {
    var table = doc.querySelector('table.dataTable, .dataTables_wrapper table, table');
    if (!table) return { here: {}, said: 0 };
    var lines = (table.innerText || '').split(/\r?\n/).map(function (s) {
      return s.replace(/\s+/g, ' ').trim();
    });
    var info = doc.querySelector('.dataTables_info');
    var said = 0;
    if (info) {
      var mm = /of\s+([\d,]+)\s+entries/i.exec(info.innerText || '');
      if (mm) said = parseInt(mm[1].replace(/,/g, ''), 10);
    }
    return { here: parseLines(lines), said: said };
  }

  /* a page that ships an empty shell is rendered and read; same origin, so its
     document is ours to read once it has settled */
  function viaFrame(url) {
    return new Promise(function (resolve) {
      var f = document.createElement('iframe');
      f.style.cssText = 'position:fixed;left:-9999px;top:0;width:1200px;height:3000px;opacity:0';
      var done = false;
      var finish = function (r) { if (done) return; done = true; f.remove(); resolve(r); };
      var timer = setTimeout(function () { finish({ here: {}, said: 0 }); }, 25000);
      f.onload = function () {
        setTimeout(function () {
          clearTimeout(timer);
          var doc = null;
          try { doc = f.contentDocument; } catch (e) { doc = null; }
          if (!doc || !doc.body) { finish({ here: {}, said: 0 }); return; }
          try {
            var sel = doc.querySelector('select[name$="_length"], .dataTables_length select');
            if (sel) {
              var best = Array.prototype.map.call(sel.options, function (o) { return parseInt(o.value, 10); })
                .filter(function (n) { return !isNaN(n); }).sort(function (a, b) { return b - a; })[0];
              if (best && String(best) !== sel.value) {
                sel.value = String(best);
                sel.dispatchEvent(new Event('change', { bubbles: true }));
              }
            }
          } catch (e) {}
          setTimeout(function () { finish(fromLive(doc)); }, 1200);
        }, 1800);
      };
      f.onerror = function () { clearTimeout(timer); finish({ here: {}, said: 0 }); };
      f.src = url;
      document.body.appendChild(f);
    });
  }

  async function readProgramme(code) {
    var urls = [
      BASE + '/PROGRAM_SITES/' + code + '/about-us/faculty-search.html',
      BASE + '/PROGRAM_SITES/' + code + '/guides/faculty.html'
    ];
    for (var i = 0; i < urls.length; i++) {
      var html = null;
      try {
        var res = await fetch(urls[i], { credentials: 'same-origin' });
        if (!res.ok) continue;
        html = await res.text();
      } catch (e) { continue; }
      var got = fromDoc(new DOMParser().parseFromString(html, 'text/html'));
      if (!Object.keys(got.here).length) {
        got = await viaFrame(urls[i]);
        got.framed = true;
      }
      if (Object.keys(got.here).length) { got.url = urls[i]; return got; }
    }
    return { here: {}, said: 0, url: urls[0] };
  }

  var roster = { generated: new Date().toISOString().slice(0, 10), source: BASE,
                 programs: {}, people: {} };
  var short = [], empty = [];
  console.log('Reading the ten GDBBS programme listings…\n');
  for (var c = 0; c < CODES.length; c++) {
    var code = CODES[c];
    var got = await readProgramme(code);
    var names = Object.keys(got.here);
    names.forEach(function (n) {
      var rec = got.here[n], was = roster.people[n];
      if (!was) {
        was = roster.people[n] = { p: [], m: {}, a: false, u: got.url, em: rec.em };
      }
      rec.p.forEach(function (k) { if (was.p.indexOf(k) < 0) was.p.push(k); });
      Object.keys(rec.m).forEach(function (k) { was.m[k] = rec.m[k]; });
      if (rec.em && !was.em) was.em = rec.em;
    });
    if (!names.length) empty.push(code);
    else if (got.said && got.said > names.length) short.push(code + ' (' + names.length + ' of ' + got.said + ')');
    console.log('  ' + code + (code.length < 4 ? '  ' : ' ') + '\t' +
      String(names.length).padStart(4) + ' read' +
      (got.said ? ' of ' + got.said + ' the table reports' : '') +
      (got.framed ? '  (rendered)' : ''));
  }
  Object.keys(roster.people).forEach(function (n) {
    roster.people[n].p.forEach(function (k) { roster.programs[k] = NAMES[k] || k; });
  });

  var all = Object.keys(roster.people);
  var full = all.filter(function (n) {
    var m = roster.people[n].m || {};
    return Object.keys(m).some(function (k) { return m[k] === 'full'; });
  }).length;
  var mailed = all.filter(function (n) { return roster.people[n].em; }).length;
  var noprog = all.filter(function (n) { return !roster.people[n].p.length; });
  console.log('\n%c' + all.length + ' people across the division%c  ·  ' + full +
    ' hold a full membership  ·  ' + mailed + ' with an email',
    'font-weight:bold', 'font-weight:normal');
  if (short.length) console.log('%cread fewer rows than the table reported: ' + short.join(', '), 'color:#c66');
  if (empty.length) console.log('%cnothing read from: ' + empty.join(', ') +
    ' — open each and run the single-programme script there', 'color:#c66');
  if (noprog.length) console.log('%cno membership line for: ' + noprog.join(', '), 'color:#c66');
  console.table(all.sort().map(function (n) {
    var r = roster.people[n];
    return { name: n, email: r.em || '', programmes: r.p.join(' '),
             membership: r.p.map(function (k) { return k + ':' + (r.m[k] || '?'); }).join(' ') };
  }));

  if (!all.length) {
    console.log('%cNothing collected. Are you on a biomed.emory.edu page?', 'color:#c66');
  } else {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(roster, null, 1)], { type: 'application/json' }));
    a.download = 'gdbbs.json';
    a.click();
    console.log('Saved gdbbs.json — load it in the atlas: Notes → Load a GDBBS roster.');
  }
})();
