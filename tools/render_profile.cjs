// GitHub API-rendered local previews for the native SVG profile.
// Add --preview-dir PATH for four browser captures (requires Playwright).
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const root = path.resolve(__dirname, '..');
const assets = path.join(root, 'assets/profile');

async function main() {
  console.log('Previewing native SVG headers and activity graphics.');
  const flag = process.argv.indexOf('--preview-dir');
  if (flag === -1) return;
  const dest = path.resolve(process.argv[flag + 1]);
  await fs.mkdir(dest, { recursive: true });
  const markdown = await fs.readFile(path.join(root, 'README.md'), 'utf8');
  const response = await fetch('https://api.github.com/markdown', {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'User-Agent': 'jeushdev-readme-preview', 'Accept': 'application/vnd.github+json' },
    body: JSON.stringify({ text: markdown, mode: 'gfm' })
  });
  if (!response.ok) throw new Error(`GitHub Markdown render: ${response.status} ${await response.text()}`);
  const rendered = await response.text();
  await fs.writeFile(path.join(dest, 'github-rendered.html'), rendered);
  const css = await fs.readFile(path.join(dest, 'github-markdown.css'), 'utf8');
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>jeushdev — Profile README preview</title><style>${css}
  body{margin:0;background:#fff}main{box-sizing:border-box;max-width:960px;margin:28px auto;padding:32px;border:1px solid #d1d9e0;border-radius:6px}
  @media(prefers-color-scheme:dark){body{background:#0d1117}main{border-color:#3d444d}}
  @media(max-width:600px){main{margin:0;border:0;border-radius:0;padding:20px}}
  </style></head><body><main class="markdown-body">${rendered}</main></body></html>`;
  await fs.writeFile(path.join(dest, 'index.html'), html);
  const mime = { '.svg':'image/svg+xml', '.png':'image/png', '.html':'text/html; charset=utf-8' };
  const server = http.createServer(async (req,res) => {
    try {
      const url = new URL(req.url,'http://localhost');
      const relative = decodeURIComponent(url.pathname);
      const file = relative.startsWith('/assets/') ? path.resolve(root,'.'+relative) : path.join(dest,'index.html');
      if (!(file.startsWith(root+path.sep)||file===path.join(dest,'index.html'))) {res.writeHead(403);res.end();return;}
      res.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');
      res.end(await fs.readFile(file));
    } catch {res.writeHead(404);res.end('Not found');}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const {chromium}=require('playwright');
  const browser=await chromium.launch({channel:'msedge',headless:true});
  const evidence=[];
  try {
    for (const [name,width,scheme] of [['desktop-dark',1280,'dark'],['mobile-dark',390,'dark'],['desktop-light',1280,'light'],['mobile-light',390,'light']]) {
      const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1,colorScheme:scheme});
      const failed=[];
      page.on('pageerror',e=>failed.push(String(e)));
      await page.goto(`http://127.0.0.1:${server.address().port}`,{waitUntil:'networkidle'});
      await page.locator('img').evaluateAll(imgs=>Promise.all(imgs.map(img=>img.decode())));
      const checks=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,images:[...document.images].map(i=>({alt:i.alt,loaded:i.complete&&i.naturalWidth>0,source:i.currentSrc.split('/').pop()})),links:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')),headings:[...document.querySelectorAll('h1,h2,h3')].map(h=>({level:h.tagName,name:h.textContent.trim()||h.querySelector('img')?.alt})),pictures:document.querySelectorAll('picture').length,sources:document.querySelectorAll('source').length}));
      await page.screenshot({path:path.join(dest, name+'.png'),fullPage:true});
      evidence.push({name,width,scheme,...checks,errors:failed});
      await page.close();
    }
    await fs.writeFile(path.join(dest,'checks.json'),JSON.stringify(evidence,null,2));
    console.log(JSON.stringify(evidence.map(({name,overflow,images,pictures,sources,errors})=>({name,overflow,images:images.length,imagesLoaded:images.every(i=>i.loaded),hero:images[0].source,pictures,sources,errors})),null,2));
  } finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
}
main().catch(e=>{console.error(e);process.exitCode=1});
