// Мини-сервер без зависимостей: отдаёт папку render3d/ и открывает страницу в браузере.
//   node serve.mjs [порт]        — http://localhost:5173/dist/index.html
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { dirname, join, normalize, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { exec } from 'node:child_process';
import { existsSync } from 'node:fs';

const ROOT = dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.argv[2] || process.env.PORT || 5173);
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.png': 'image/png', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml' };

createServer(async (req, res) => {
  try {
    let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (p === '/') p = '/dist/index.html';
    const file = normalize(join(ROOT, p));
    if (!file.startsWith(ROOT)) { res.writeHead(403).end(); return; }
    if ((await stat(file)).isDirectory()) { res.writeHead(302, { Location: p.replace(/\/?$/, '/') + 'index.html' }).end(); return; }
    res.writeHead(200, { 'Content-Type': TYPES[extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(await readFile(file));
  } catch { res.writeHead(404).end('Not found'); }
}).on('error', e => {
  if (e.code !== 'EADDRINUSE') throw e;
  console.error(`Порт ${PORT} занят (возможно, сервер уже запущен). Другой порт: npm start -- ${PORT + 1}`); process.exit(1);
}).listen(PORT, () => {
  // если three.js уже установлен (npm install) — открываем офлайн-версию: не зависит от доступности CDN
  const local = existsSync(join(ROOT, 'node_modules/three/build/three.module.js'));
  const url = `http://localhost:${PORT}/dist/${local ? 'local' : 'index'}.html`;
  console.log(`Участок 3D: ${url}\n(версия с CDN: http://localhost:${PORT}/dist/index.html · офлайн: http://localhost:${PORT}/dist/local.html)\nОстановить — Ctrl+C`);
  if (!process.env.NO_OPEN) {
    const cmd = process.platform === 'win32' ? `start "" "${url}"` : process.platform === 'darwin' ? `open "${url}"` : `xdg-open "${url}"`;
    exec(cmd, () => {});
  }
});
