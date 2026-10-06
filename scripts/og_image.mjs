// node scripts/og_image.mjs og-image.png [investigators] [placed]
// Renders the 1200x630 image link previews show (GroupMe, Slack, iMessage, search results).
import { chromium } from 'playwright';
const [out = 'og-image.png', total = '7,078', placed = '5,170'] = process.argv.slice(2);
const html = `<!doctype html><html><body style="margin:0">
<div style="width:1200px;height:630px;box-sizing:border-box;padding:72px 80px;background:#031b36;color:#fdffee;font-family:Inter,system-ui,sans-serif;display:flex;flex-direction:column;justify-content:space-between">
  <div style="display:flex;align-items:center;gap:16px;font-size:30px;font-weight:600">
    <svg width="52" height="52" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#0b2c52"/><path d="M7 16h18" stroke="#fdffee" stroke-width="2" stroke-linecap="round" opacity=".55"/>
    <circle cx="8" cy="16" r="3.4" fill="#cf5f49"/><circle cx="16" cy="16" r="3.4" fill="#c9a2f2"/><circle cx="24" cy="16" r="3.4" fill="#3b8ccc"/></svg>Emory Lab Atlas</div>
  <div>
    <div style="font-size:76px;font-weight:700;line-height:1.02;letter-spacing:-2px">Find an Emory lab<br>that fits you.</div>
    <div style="font-size:34px;margin-top:22px;color:#3fb6e8">Know if it&rsquo;s bench or computer work before you email.</div>
  </div>
  <div style="display:flex;gap:6px;height:16px;border-radius:8px;overflow:hidden">
    <i style="flex:11;background:#cf5f49"></i><i style="flex:1.4;background:#c9a2f2"></i><i style="flex:60;background:#3b8ccc"></i><i style="flex:27;background:#56657a"></i></div>
  <div style="font-size:24px;color:rgba(253,255,238,.75)">${total} investigators &middot; ${placed} placed from their papers and grants &middot; free for Emory students</div>
</div></body></html>`;
const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1200,height:630}});
await p.setContent(html); await p.screenshot({path: out}); await b.close();
console.log('wrote', out);
