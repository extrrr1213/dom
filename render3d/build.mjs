// Сборка страницы 3D-визуализации:
//   dist/index.html — для браузера и публикации (three.js с CDN jsdelivr, нужен интернет);
//   dist/local.html — без интерфейса, three.js из node_modules (для офлайн-просмотра и рендера кадров).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const THREE_VER = '0.160.0';
const read = f => readFileSync(join(HERE, f), 'utf8');

const importmap = base => JSON.stringify({ imports: { three: `${base}/build/three.module.js`, 'three/addons/': `${base}/examples/jsm/` } });
const sceneJs = read('scene.js'), data = read('scene.json'), page = read('page.html');
const tail = base => `<script type="importmap">${importmap(base)}</script><script>window.SCENE = ${data};</script>` +
  `<script type="module">\n${sceneJs}\n</script>`;

const pages = {
  'dist/index.html': page + tail(`https://cdn.jsdelivr.net/npm/three@${THREE_VER}`),
  'dist/local.html': '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Участок 3D (локально)</title>' +
    page + tail('/node_modules/three'),
  'dist/render.html': '<!doctype html><meta charset=utf-8><title>render</title>' +
    '<style>html,body{margin:0;height:100%;background:#cfdbe6}#c{display:block;width:100vw;height:100vh}</style><canvas id="c"></canvas>' +
    tail('/node_modules/three'),
};
mkdirSync(join(HERE, 'dist'), { recursive: true });
for (const [f, html] of Object.entries(pages)) {
  writeFileSync(join(HERE, f), html);
  console.log('→', f, `${Math.round(html.length / 1024)} KB`);
}
