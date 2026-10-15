/**
 * Lab Atlas -> Google Drive publisher (Google Apps Script).
 *
 * Once an hour this checks the GitHub repository for the newest
 * Emory_Lab_Atlas_vNN.html. If the shared "Emory Lab Atlas" folder does not have
 * that version yet, it copies the file in and adds a row to the folder's
 * "Lab Atlas versions.md". Every later version is picked up the same way, with
 * nothing to run by hand.
 *
 * It keeps the same bookkeeping file (.labatlas-sync.json) as
 * scripts/drive_sync.py, so the two never upload the same version twice, and
 * drive_sync.py's merge step never mistakes a version published here for a
 * collaborator's file.
 *
 * Setup, once, signed in to Google as someone who can edit the folder:
 *   1. Open https://script.google.com and choose "New project".
 *   2. Replace the editor's contents with this file, and save.
 *   3. In the function menu next to "Debug", choose `install` and press Run.
 *      Allow the access it asks for: Drive, to write to the folder, and
 *      external requests, to read the repository.
 * install publishes the current version straight away and schedules the hourly
 * check. To stop, run `uninstall`.
 *
 * Limits: Apps Script can fetch and save files up to 50 MB. The atlas is
 * about 38 MB today. If it grows past 50 MB, publish with drive_sync.py from
 * the GitHub workflow instead (scripts/README.md, "Google Drive sync").
 */
const CONFIG = {
  folderId: '14_ZcVAechYZ-Hqbex3s2IdGag2GuU3gG',   // "Emory Lab Atlas"
  repo: 'cpratapaneni-beep/LabAtlas-',
  // the newest version on any of these branches is published
  branches: ['claude/exciting-carson-83od2i', 'main'],
  everyHours: 1,
};
const STATE_NAME = '.labatlas-sync.json';
const LOG_NAME = 'Lab Atlas versions.md';
const ATLAS_RE = /^Emory_Lab_Atlas_v(\d+)\.html$/;

function install() {
  uninstall();
  ScriptApp.newTrigger('publishLatest').timeBased().everyHours(CONFIG.everyHours).create();
  publishLatest();
}

function uninstall() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'publishLatest')
    .forEach(t => ScriptApp.deleteTrigger(t));
}

function publishLatest() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) return;
  try {
    const folder = DriveApp.getFolderById(CONFIG.folderId);
    const state = readState_(folder);
    const latest = findLatest_(state);
    if (!latest) { console.log('No atlas file found on ' + CONFIG.branches.join(', ')); return; }

    // already published from this exact commit of the file
    const seen = Object.keys(state.pushed).some(k => state.pushed[k].name === latest.name && state.pushed[k].sha && state.pushed[k].sha === latest.sha);
    if (seen) { console.log(latest.name + ' is already in the folder'); return; }

    const res = UrlFetchApp.fetch(latest.url, {muteHttpExceptions: true});
    if (res.getResponseCode() !== 200) throw new Error('Could not download ' + latest.name + ': HTTP ' + res.getResponseCode());
    const blob = res.getBlob().setName(latest.name).setContentType('text/html');
    const md5 = md5_(blob.getBytes());

    // the same bytes may already be there (published by drive_sync.py, or by hand)
    if (state.pushed[md5]) {
      state.pushed[md5].sha = latest.sha;
      writeState_(folder, state);
      console.log(latest.name + ' is already in the folder');
      return;
    }
    const twins = folder.getFilesByName(latest.name);
    while (twins.hasNext()) {
      const f = twins.next();
      if (md5_(f.getBlob().getBytes()) === md5) {
        record_(state, md5, latest, f.getId(), 'already in the folder');
        writeState_(folder, state); writeLog_(folder, state);
        console.log(latest.name + ' was already in the folder; recorded it');
        return;
      }
    }

    const file = folder.createFile(blob);
    file.setDescription('Emory Lab Atlas ' + latest.name.replace(/^Emory_Lab_Atlas_|\.html$/g, '') +
                        ', published from GitHub (' + latest.branch + (latest.commit ? ' @ ' + latest.commit : '') + ')');
    record_(state, md5, latest, file.getId(), 'published from GitHub');
    writeState_(folder, state);
    writeLog_(folder, state);
    console.log('Published ' + latest.name);
  } finally {
    lock.releaseLock();
  }
}

/* The newest Emory_Lab_Atlas_vNN.html across the branches. The listing comes
   from GitHub's API. If that is rate limited, the next version numbers after
   the newest one already published are tried directly. */
function findLatest_(state) {
  let best = null;
  CONFIG.branches.forEach(branch => {
    const list = gh_('/contents?ref=' + encodeURIComponent(branch));
    if (!Array.isArray(list)) return;
    list.forEach(f => {
      const m = f.type === 'file' && ATLAS_RE.exec(f.name);
      if (m && (!best || +m[1] > best.v)) best = {v: +m[1], name: f.name, sha: f.sha, url: f.download_url, branch};
    });
  });
  if (!best) {
    const top = Math.max(0, ...Object.keys(state.pushed).map(k => +((ATLAS_RE.exec(state.pushed[k].name) || [])[1] || 0)));
    for (const branch of CONFIG.branches) {
      for (let v = top + 3; v > top && !best; v--) {
        const name = 'Emory_Lab_Atlas_v' + v + '.html';
        const url = 'https://raw.githubusercontent.com/' + CONFIG.repo + '/' + branch + '/' + name;
        const r = UrlFetchApp.fetch(url, {method: 'get', headers: {Range: 'bytes=0-0'}, muteHttpExceptions: true});
        if (r.getResponseCode() === 200 || r.getResponseCode() === 206) best = {v, name, sha: '', url, branch};
      }
      if (best) break;
    }
  }
  if (best) {
    const c = gh_('/commits?per_page=1&sha=' + encodeURIComponent(best.branch) + '&path=' + encodeURIComponent(best.name));
    best.commit = Array.isArray(c) && c[0] ? c[0].sha.slice(0, 7) : '';
  }
  return best;
}

function gh_(path) {
  const r = UrlFetchApp.fetch('https://api.github.com/repos/' + CONFIG.repo + path,
    {headers: {Accept: 'application/vnd.github+json'}, muteHttpExceptions: true});
  if (r.getResponseCode() !== 200) { console.log('GitHub ' + r.getResponseCode() + ' for ' + path); return null; }
  return JSON.parse(r.getContentText());
}

function md5_(bytes) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, bytes)
    .map(b => ('0' + (b & 0xff).toString(16)).slice(-2)).join('');
}

function record_(state, md5, latest, id, note) {
  state.pushed[md5] = {name: latest.name, id: id, at: new Date().toISOString(), commit: latest.commit || '', note: note, sha: latest.sha || ''};
}

function readState_(folder) {
  const it = folder.getFilesByName(STATE_NAME);
  if (!it.hasNext()) return {pushed: {}, merged: {}};
  const s = JSON.parse(it.next().getBlob().getDataAsString() || '{}');
  s.pushed = s.pushed || {}; s.merged = s.merged || {};
  return s;
}

function writeState_(folder, state) {
  const keys = o => Object.keys(o).sort().reduce((a, k) => (a[k] = o[k], a), {});
  const text = JSON.stringify({merged: keys(state.merged), pushed: keys(state.pushed)}, null, 1);
  put_(folder, STATE_NAME, text, 'application/json');
}

/* The version log, written exactly as drive_sync.py writes it. */
function writeLog_(folder, state) {
  const rows = [];
  Object.keys(state.pushed).forEach(k => { const v = state.pushed[k]; rows.push([v.at, v.name, 'repository ' + (v.commit || ''), v.note || '']); });
  Object.keys(state.merged).forEach(k => { const v = state.merged[k]; rows.push([v.at, v.name, 'the folder' + (v.by ? ' (' + v.by + ')' : ''), 'merged into ' + (v.into || '')]); });
  rows.sort((a, b) => a[0] < b[0] ? 1 : a[0] > b[0] ? -1 : 0);
  const lines = ['# Lab Atlas versions\n', 'Newest first. Every version the pipeline publishes, and every file merged in from this folder.\n',
                 '| Version | Published (UTC) | From | Note |', '|---|---|---|---|']
    .concat(rows.map(r => '| ' + r[1] + ' | ' + r[0].slice(0, 16).replace('T', ' ') + ' | ' + r[2] + ' | ' + r[3] + ' |'));
  put_(folder, LOG_NAME, lines.join('\n') + '\n', 'text/markdown');
}

function put_(folder, name, text, mime) {
  const it = folder.getFilesByName(name);
  if (it.hasNext()) it.next().setContent(text);
  else folder.createFile(name, text, mime);
}
