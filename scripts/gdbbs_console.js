/* Emory GDBBS faculty, read from a programme's own faculty page.
 *
 * Open a programme's faculty listing, for example
 *   https://biomed.emory.edu/PROGRAM_SITES/BCDB/about-us/faculty-search.html
 * paste this whole file into the console (F12) and press Enter.
 *
 * It reads the Faculty Listing table. Each entry gives a name, an Emory email,
 * and one line per GDBBS programme the person belongs to saying whether that
 * membership is full, affiliate or adjunct. Because every entry lists all of
 * its memberships, one page already carries programme data for everybody on
 * it; run it on each programme page to cover the division. Results accumulate
 * and gdbbs.json is downloaded each time.
 *
 * On what "full" means, in this page's own words: the three memberships are
 * Full, Affiliate and Adjunct, and Full Graduate Faculty are the ones who may
 * act as dissertation advisors. That is the closest the page comes to saying
 * somebody takes graduate students. It is not a statement that they are
 * recruiting this year, and it is not recorded as one.
 *
 * Every comment here is a block comment and nothing returns at the top level,
 * so this still runs if your clipboard flattens it onto a single line - which
 * is what "Illegal return statement" and a VM:1 column number mean.
 */
(async function () {
  var STORE = 'gdbbs-collect';
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
  var DEGREE = /^(PHD|MD|DVM|DDS|SCD|MPH|MS|MSC|MBBS|PHARMD|RN|DPHIL|DO|MBA|JD|MA|BS|BA|MSN|DNP|DRPH|MSPH|FAAN|FACS|FAHA|FACC)$/;
  /* capitalised words that are page furniture rather than somebody's name */
  var NOTNAME = /\b(FACULTY|MEMBERSHIP|MEMBER|LISTING|SEARCH|RESET|FORM|MENU|SHOW|ENTRIES|PREVIOUS|NEXT|EMORY|GDBBS|PROGRAM|GRADUATE|ADJUNCT|AFFILIATE|FULL|PROFILE|WEBSITE|LAB|DEPARTMENT|SCHOOL|UNIVERSITY|CONTACT|ABOUT|HOME|APPLY|RESOURCES|STUDENTS|ALUMNI|NEWS|EVENTS)\b/;

  /* "FIKRI AVCI, PHD (HE/HIM)" -> "Fikri Avci". The listing is upper case
     throughout, so case cannot find a name here; the shape has to. */
  function readName(line) {
    var s = String(line || '').trim();
    if (!s || s.length > 90 || s.indexOf('@') >= 0 || /\d/.test(s)) return null;
    if (/\bMEMBER\s*[-–]/.test(s)) return null;
    s = s.replace(/\([^)]*\)/g, '').trim();
    var parts = s.split(',').map(function (x) { return x.trim(); }).filter(Boolean);
    if (!parts.length) return null;
    /* anything after the first comma has to be a degree, or this is prose */
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
    var title = base.toLowerCase().replace(/(^|[\s'\u2019\-])([a-z])/g,
      function (m, a, b) { return a + b.toUpperCase(); });
    /* A lone letter standing as its own word is an initial and takes a stop.
       A letter against an apostrophe is not: L'HERNAULT is L'Hernault, and
       dotting every single letter made it L.'Hernault. */
    title = title.replace(/(^|\s)([A-Za-z])(?=\s|$)/g,
      function (m, a, c) { return a + c.toUpperCase() + '.'; });
    /* Mc is always a prefix, so McCarty and McKimpson come back right. Mac is
       not - Macey and Machado are surnames - so it is left alone. */
    title = title.replace(/\bMc([a-z])/g, function (m, c) { return 'Mc' + c.toUpperCase(); });
    /* a nobiliary particle stays lower case: van der Berg, not Van Der Berg */
    title = title.replace(/\b(Van|Von|Der|Den|Del|Della|De|Da|Di|Dos|Du|La|Le|Ter|Ten)\b(?!\.)/g,
      function (m, w, off) { return off === 0 ? m : m.toLowerCase(); });
    return title.replace(/\.\./g, '.');
  }

  /* show every row before reading, so nobody is stranded on page two */
  function showAll() {
    var sel = document.querySelector('select[name$="_length"], .dataTables_length select');
    if (!sel) return 0;
    var best = Array.prototype.map.call(sel.options, function (o) { return parseInt(o.value, 10); })
      .filter(function (n) { return !isNaN(n); }).sort(function (a, b) { return b - a; })[0];
    if (!best || String(best) === sel.value) return 0;
    sel.value = String(best);
    sel.dispatchEvent(new Event('change', { bubbles: true }));
    return best;
  }

  function parseTable(table) {
    var lines = (table.innerText || '').split(/\r?\n/).map(function (s) {
      return s.replace(/\s+/g, ' ').trim();
    });
    var here = {}, cur = null;
    lines.forEach(function (line) {
      var mem = /^(FULL|AFFILIATE|ADJUNCT)\s+MEMBER\s*[-–]\s*(.+)$/i.exec(line);
      if (mem && cur) {
        var code = PROGRAMS[mem[2].trim().toUpperCase()];
        if (code) {
          if (cur.p.indexOf(code) < 0) cur.p.push(code);
          cur.m[code] = mem[1].toLowerCase();
        } else {
          cur.unknown = (cur.unknown || []).concat(mem[2].trim());
        }
        return;
      }
      var mail = /([\w.\-+]+@[\w.\-]*emory\.edu)/i.exec(line);
      if (mail && cur && !cur.em) { cur.em = mail[1].toLowerCase(); return; }
      var name = readName(line);
      if (name) {
        if (!here[name]) here[name] = { p: [], m: {}, a: false, u: location.href };
        cur = here[name];
      }
    });
    return here;
  }

  function merge(here) {
    var roster = null;
    try { roster = JSON.parse(localStorage.getItem(STORE)); } catch (e) { roster = null; }
    if (!roster || !roster.people) {
      roster = { generated: '', source: location.origin, programs: {}, people: {} };
    }
    roster.generated = new Date().toISOString().slice(0, 10);
    var fresh = 0;
    Object.keys(here).forEach(function (name) {
      var rec = here[name], was = roster.people[name];
      if (!was) { roster.people[name] = rec; fresh++; return; }
      rec.p.forEach(function (c) { if (was.p.indexOf(c) < 0) was.p.push(c); });
      was.m = was.m || {};
      Object.keys(rec.m).forEach(function (c) { was.m[c] = rec.m[c]; });
      if (rec.em && !was.em) was.em = rec.em;
    });
    Object.keys(roster.people).forEach(function (n) {
      (roster.people[n].p || []).forEach(function (c) { roster.programs[c] = NAMES[c] || c; });
    });
    try { localStorage.setItem(STORE, JSON.stringify(roster)); } catch (e) {}
    return { roster: roster, fresh: fresh };
  }

  function report(here, roster, fresh) {
    var found = Object.keys(here).length;
    var people = Object.keys(roster.people).map(function (n) { return roster.people[n]; });
    var full = people.filter(function (r) {
      return Object.keys(r.m || {}).some(function (c) { return r.m[c] === 'full'; });
    }).length;
    var mailed = people.filter(function (r) { return r.em; }).length;
    console.log('%c' + found + ' on this page%c  ·  ' + fresh + ' new  ·  ' +
      people.length + ' collected so far  ·  ' + full + ' hold a full membership  ·  ' +
      mailed + ' with an email', 'font-weight:bold', 'font-weight:normal');
    console.table(Object.keys(here).map(function (n) {
      var r = here[n];
      return { name: n, email: r.em || '', programs: r.p.join(' '),
               membership: r.p.map(function (c) { return c + ':' + (r.m[c] || '?'); }).join(' ') };
    }));
    var info = document.querySelector('.dataTables_info');
    if (info) {
      var said = info.innerText.trim();
      console.log('table said:', said);
      var mm = /of\s+([\d,]+)\s+entries/i.exec(said);
      if (mm && parseInt(mm[1].replace(/,/g, ''), 10) > found) {
        console.log('%c' + (parseInt(mm[1].replace(/,/g, ''), 10) - found) + ' of the ' + mm[1] +
          ' rows were not read as people. Say so and I will look at why.', 'color:#c66');
      }
    }
    var noprog = Object.keys(here).filter(function (n) { return !here[n].p.length; });
    if (noprog.length) {
      console.log('%cNo membership line found for: ' + noprog.join(', ') +
        ' \u2014 on the roster, but with no programme against them.', 'color:#c66');
    }
    var unknown = [];
    Object.keys(here).forEach(function (n) {
      (here[n].unknown || []).forEach(function (u) { if (unknown.indexOf(u) < 0) unknown.push(u); });
    });
    if (unknown.length) console.log('%cUnrecognised programme names: ' + unknown.join(' | '), 'color:#c66');
  }

  function save(roster) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(roster, null, 1)], { type: 'application/json' }));
    a.download = 'gdbbs.json';
    a.click();
    console.log('Saved gdbbs.json. Repeat on the other programme pages, then load it in the atlas: ' +
      'Notes → Load a GDBBS roster.   (GDBBS_RESET() to start over.)');
  }

  var bumped = showAll();
  if (bumped) {
    console.log('Set the table to show ' + bumped + ' rows; waiting for it to redraw…');
    await new Promise(function (r) { setTimeout(r, 1200); });
  }
  var table = document.querySelector('table.dataTable, .dataTables_wrapper table, table');
  if (!table) {
    console.log('%cNo faculty table on this page. Is the Faculty Listing on screen?', 'color:#c66');
  } else {
    var here = parseTable(table);
    var merged = merge(here);
    report(here, merged.roster, merged.fresh);
    if (!Object.keys(here).length) {
      console.log('%cNothing read from the table.', 'color:#c66');
    } else {
      save(merged.roster);
    }
  }
  window.GDBBS_RESET = function () { localStorage.removeItem(STORE); console.log('Cleared.'); };
})();
