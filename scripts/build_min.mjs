import { minify } from 'terser';
import { readFileSync, writeFileSync } from 'node:fs';
for (const [src, out, label] of [
  ['/home/user/LabAtlas-/scripts/gdbbs_all.js',     '/home/user/LabAtlas-/scripts/gdbbs_all.min.js',     'all ten programmes'],
  ['/home/user/LabAtlas-/scripts/gdbbs_console.js', '/home/user/LabAtlas-/scripts/gdbbs_console.min.js', 'one programme, the page you are on'],
]) {
  const code = readFileSync(src, 'utf8');
  const r = await minify(code, {
    compress: { drop_console: false },
    mangle: true,
    format: { comments: false, beautify: false },
  });
  if (r.error) throw r.error;
  const one = r.code.replace(/\n/g, ' ').trim();
  if (one.includes('\n')) throw new Error('not one line');
  writeFileSync(out, one + '\n');
  console.log(`${label.padEnd(36)} ${code.length} chars -> ${one.length} on one line`);
}
