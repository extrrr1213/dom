// 3D-визуализация участка (ИЖС, Одинцово, ул. 1905 года) по геометрии из plan.py → scene.json.
// План: x — на восток (к улице), y — на север. three.js: X = x, Z = −y, Y — вверх.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Sky } from 'three/addons/objects/Sky.js';

const S = window.SCENE;
const params = new URLSearchParams(location.search);
const HQ = !!window.HQ || params.has('hq');

// ---------- детерминированный «рандом» ----------
let seed = 20261007;
function rnd() {
  seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}
const rr = (a, b) => a + (b - a) * rnd();

// ---------- координаты ----------
const cx = S.plot.reduce((s, p) => s + p[0], 0) / S.plot.length;
const cy = S.plot.reduce((s, p) => s + p[1], 0) / S.plot.length;
const X = x => x - cx;
const Z = y => -(y - cy);
const V = (x, y, h = 0) => new THREE.Vector3(X(x), h, Z(y));
const HX0 = S.house.x0, HY0 = S.house.y0;
const L = (lx, ly) => [HX0 + lx, HY0 + ly];          // локальные координаты дома → план

// ---------- рендерер / сцена ----------
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: !HQ, preserveDrawingBuffer: HQ });
renderer.setPixelRatio(HQ ? 1 : Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.shadowMap.autoUpdate = false;     // сцена статична — тени пересчитываем только при смене солнца
let dirty = true;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.62;
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0xffffff, 0.0025);                // дымка: лес в 240 м ≈ 30 %
scene.fog.color.setRGB(0.8, 0.95, 1.2, THREE.LinearSRGBColorSpace);  // линейные >0.5 ≈ яркость горизонта после экспозиции
const camera = new THREE.PerspectiveCamera(42, 1, 0.3, 6000);

// ---------- процедурные текстуры ----------
function canvasTex(size, draw, { srgb = true, w = size, h = size } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}
const hsl = (h, s, l, a = 1) => `hsla(${h},${s}%,${l}%,${a})`;
function noise(g, w, h, n, colorFn, sz = 2) {
  for (let i = 0; i < n; i++) { g.fillStyle = colorFn(); g.fillRect(rnd() * w, rnd() * h, sz, sz); }
}
function grassDraw(stripes, hue = 86, sat = 30, dry = 0) {
  return (g, w, h) => {
    g.fillStyle = hsl(hue, sat, 30); g.fillRect(0, 0, w, h);
    for (let i = 0; i < 30; i++) {               // крупные пятна
      const x = rnd() * w, y = rnd() * h, r = rr(20, 110); const gr = g.createRadialGradient(x, y, 0, x, y, r);
      gr.addColorStop(0, hsl(hue + rr(-14, 10) - dry * rnd() * 30, sat + rr(-8, 8), rr(25, 38), 0.4)); gr.addColorStop(1, hsl(hue, sat, 30, 0));
      g.fillStyle = gr; for (const ox of [-w, 0, w]) for (const oy of [-h, 0, h]) { g.save(); g.translate(ox, oy); g.fillRect(x - r, y - r, 2 * r, 2 * r); g.restore(); }
    }
    for (let i = 0, nb = 52000 * (w / 1024) ** 2; i < nb; i++) {             // травинки
      const x = rnd() * w, y = rnd() * h, a = rr(-0.7, 0.7) - Math.PI / 2, l = rr(2, 7);
      const hh = hue + rr(-16, 14) - (rnd() < dry ? rr(15, 40) : 0);
      g.strokeStyle = hsl(hh, rr(sat - 12, sat + 14), rr(18, 46), rr(0.45, 0.9));
      g.lineWidth = rr(0.6, 1.3); g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
    }
    if (stripes) {                                // полосы от газонокосилки
      g.fillStyle = 'rgba(255,255,220,0.045)'; g.fillRect(0, 0, w, h / 2);
      g.fillStyle = 'rgba(0,15,0,0.045)'; g.fillRect(0, h / 2, w, h / 2);
    }
  };
}
// листва: «карточки» с прорисованными листьями (альфа)
function leafDraw(hue, sat, kind = 'leaf') {
  return (g, w, h) => {
    g.clearRect(0, 0, w, h);
    const n = kind === 'needle' ? 700 : 300;
    for (let i = 0; i < n; i++) {
      const x = rr(0.12, 0.88) * w, y = rr(0.12, 0.88) * h;
      g.save(); g.translate(x, y); g.rotate(rr(0, 6.28));
      g.fillStyle = hsl(hue + rr(-10, 10), sat + rr(-10, 10), rr(20, 46));
      if (kind === 'needle') { g.fillRect(-1, -rr(8, 16), 2.2, rr(16, 30)); }
      else { g.beginPath(); g.ellipse(0, 0, rr(9, 15), rr(5, 8), 0, 0, 6.28); g.fill();
        g.strokeStyle = 'rgba(0,0,0,0.15)'; g.lineWidth = 0.8; g.beginPath(); g.moveTo(-9, 0); g.lineTo(9, 0); g.stroke(); }
      g.restore();
    }
  };
}
const T = {
  lawn: canvasTex(HQ ? 1024 : 512, grassDraw(true, 88, 30)),
  meadow: canvasTex(HQ ? 1024 : 512, grassDraw(false, 76, 26, 0.12)),
  macro: canvasTex(256, (g, w, h) => {            // крупная неоднородность травы (как aoMap)
    g.fillStyle = '#d0d0d0'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 60; i++) {
      const x = rnd() * w, y = rnd() * h, r = rr(15, 70), gr = g.createRadialGradient(x, y, 0, x, y, r);
      const v = rnd() < 0.5 ? 120 : 255; gr.addColorStop(0, `rgba(${v},${v},${v},0.55)`); gr.addColorStop(1, `rgba(${v},${v},${v},0)`);
      g.fillStyle = gr; for (const ox of [-w, 0, w]) for (const oy of [-h, 0, h]) { g.save(); g.translate(ox, oy); g.fillRect(x - r, y - r, 2 * r, 2 * r); g.restore(); }
    }
  }, { srgb: false }),
  leaf: canvasTex(256, leafDraw(95, 45)),
  leafLight: canvasTex(256, leafDraw(80, 50)),
  needle: canvasTex(256, leafDraw(130, 35, 'needle')),
  deck: canvasTex(512, (g, w, h) => {             // лиственница, 7 досок по 0.14 м на 1 м
    const n = 7, bh = h / n;
    for (let i = 0; i < n; i++) {
      g.fillStyle = hsl(rr(24, 30), rr(42, 52), rr(40, 50)); g.fillRect(0, i * bh, w, bh);
      for (let k = 0; k < 40; k++) {
        g.strokeStyle = hsl(22, 50, rr(25, 35), rr(0.08, 0.2)); g.lineWidth = rr(0.5, 1.6);
        const y = i * bh + rr(3, bh - 3); g.beginPath(); g.moveTo(0, y);
        for (let x = 0; x <= w; x += 32) g.lineTo(x, y + Math.sin(x / rr(30, 90) + k) * rr(0.5, 2));
        g.stroke();
      }
      g.fillStyle = 'rgba(30,18,8,0.85)'; g.fillRect(0, i * bh, w, 3);
      const off = rr(0, w); g.fillRect(off, i * bh, 2, bh);  // стык досок
    }
  }),
  clad: canvasTex(512, (g, w, h) => {             // графитовый фиброцемент, доска 0.2 м
    g.fillStyle = '#3a3d41'; g.fillRect(0, 0, w, h);
    noise(g, w, h, 9000, () => hsl(210, 4, rr(20, 30), 0.25));
    const n = 5, bw = w / n;
    for (let i = 0; i < n; i++) {
      g.fillStyle = 'rgba(0,0,0,0.55)'; g.fillRect(i * bw, 0, 3, h);
      g.fillStyle = 'rgba(255,255,255,0.05)'; g.fillRect(i * bw + 3, 0, 2, h);
    }
  }),
  slats: canvasTex(512, (g, w, h) => {            // термодерево, рейка 0.09 м
    const n = 11, bw = w / n;
    for (let i = 0; i < n; i++) {
      g.fillStyle = hsl(rr(22, 27), rr(40, 50), rr(30, 38)); g.fillRect(i * bw, 0, bw, h);
      for (let k = 0; k < 14; k++) {
        g.strokeStyle = hsl(20, 45, rr(18, 26), rr(0.12, 0.3)); g.lineWidth = rr(0.5, 1.2);
        const x = i * bw + rr(3, bw - 3); g.beginPath(); g.moveTo(x, 0); g.lineTo(x + rr(-2, 2), h); g.stroke();
      }
      g.fillStyle = 'rgba(15,8,4,0.9)'; g.fillRect(i * bw, 0, 5, h);
    }
  }),
  pavers: canvasTex(512, (g, w, h) => {           // брусчатка 0.2 × 0.1 м, перевязка
    g.fillStyle = '#6d6a62'; g.fillRect(0, 0, w, h);
    const pw = w / 5, ph = h / 10;
    for (let r = 0; r < 10; r++) for (let c = -1; c < 6; c++) {
      const x = c * pw + (r % 2 ? pw / 2 : 0);
      g.fillStyle = hsl(rr(35, 45), rr(4, 9), rr(52, 64)); g.fillRect(x + 2, r * ph + 2, pw - 4, ph - 4);
    }
    noise(g, w, h, 7000, () => hsl(40, 5, rr(35, 75), 0.18));
  }),
  asphalt: canvasTex(512, (g, w, h) => {
    g.fillStyle = '#45474a'; g.fillRect(0, 0, w, h);
    noise(g, w, h, 30000, () => hsl(220, 3, rr(20, 60), 0.35), 2);
    for (let i = 0; i < 4; i++) {                 // мягкие заплатки неправильной формы
      const x0 = rnd() * w, y0 = rnd() * h, R = rr(25, 80); g.fillStyle = hsl(220, 3, rr(24, 32), 0.25); g.beginPath();
      for (let k = 0; k < 7; k++) { const a = k / 7 * 6.28, rr_ = R * rr(0.6, 1); g.lineTo(x0 + Math.cos(a) * rr_ * 1.6, y0 + Math.sin(a) * rr_); }
      g.fill();
    }
    g.strokeStyle = 'rgba(20,20,20,0.35)'; g.lineWidth = 1;
    for (let i = 0; i < 6; i++) { let x = rnd() * w, y = rnd() * h; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 8; k++) { x += rr(-14, 14); y += rr(-14, 14); g.lineTo(x, y); } g.stroke(); }
  }),
  gravel: canvasTex(256, (g, w, h) => {
    g.fillStyle = '#7d756a'; g.fillRect(0, 0, w, h);
    noise(g, w, h, 9000, () => hsl(rr(25, 40), rr(5, 15), rr(35, 70), 0.6), 3);
  }),
  tiles: canvasTex(512, (g, w, h) => {            // мозаика бассейна 0.05 м
    g.fillStyle = '#e9f3f3'; g.fillRect(0, 0, w, h);
    const n = 20, s = w / n;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      g.fillStyle = hsl(rr(186, 196), rr(50, 70), rr(52, 66)); g.fillRect(i * s + 1.5, j * s + 1.5, s - 3, s - 3);
    }
  }),
  stone: canvasTex(256, (g, w, h) => {            // бортик бассейна, светлый камень
    g.fillStyle = '#cfccc4'; g.fillRect(0, 0, w, h);
    noise(g, w, h, 8000, () => hsl(40, 6, rr(60, 90), 0.4));
    g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(0, 0, w, 2); g.fillRect(0, 0, 2, h);
  }),
  rubber: canvasTex(256, (g, w, h) => {           // резиновое покрытие площадки
    g.fillStyle = '#2f6f63'; g.fillRect(0, 0, w, h);
    noise(g, w, h, 14000, () => hsl(rr(160, 175), rr(25, 45), rr(22, 42), 0.7), 2);
  }),
  sand: canvasTex(256, (g, w, h) => {
    g.fillStyle = '#d9c38f'; g.fillRect(0, 0, w, h);
    noise(g, w, h, 14000, () => hsl(rr(38, 46), rr(30, 50), rr(60, 85), 0.6), 2);
  }),
  roofMembrane: canvasTex(256, (g, w, h) => {
    g.fillStyle = '#5d6063'; g.fillRect(0, 0, w, h);
    noise(g, w, h, 6000, () => hsl(210, 3, rr(30, 50), 0.4), 2);
    g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(0, 0, w, 2);
  }),
  mesh: canvasTex(128, (g, w, h) => {             // 3D-сетка 200 × 50 мм (плитка 0.4 м)
    g.clearRect(0, 0, w, h); g.fillStyle = '#2c4a34';
    g.fillRect(0, 0, 3, h); g.fillRect(w / 2, 0, 3, h);
    for (let y = 0; y < h; y += 16) g.fillRect(0, y, w, 2);
  }, { srgb: true }),
  ranch: canvasTex(512, (g, w, h) => {            // забор-ранчо: ламели 0.1 м, просвет 0.02 м (плитка 0.6 м)
    g.clearRect(0, 0, w, h);
    const n = 5, ph = h / n;
    for (let i = 0; i < n; i++) {
      const gr = g.createLinearGradient(0, i * ph, 0, i * ph + ph * 0.83);
      gr.addColorStop(0, '#4a4d51'); gr.addColorStop(0.5, '#3a3d41'); gr.addColorStop(1, '#2c2f33');
      g.fillStyle = gr; g.fillRect(0, i * ph, w, ph * 0.83);
    }
  }),
  siding: canvasTex(256, (g, w, h) => {           // сайдинг соседей (тонируется цветом материала)
    g.fillStyle = '#f2f0ea'; g.fillRect(0, 0, w, h);
    const n = 5, ph = h / n;
    for (let i = 0; i < n; i++) {
      const gr = g.createLinearGradient(0, i * ph, 0, (i + 1) * ph);
      gr.addColorStop(0, 'rgba(0,0,0,0.18)'); gr.addColorStop(0.15, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.05)');
      g.fillStyle = gr; g.fillRect(0, i * ph, w, ph);
    }
  }),
  metalRoof: canvasTex(256, (g, w, h) => {        // металлочерепица (тонируется)
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, w, h);
    const n = 8, bw = w / n;
    for (let i = 0; i < n; i++) {
      const gr = g.createLinearGradient(i * bw, 0, (i + 1) * bw, 0);
      gr.addColorStop(0, 'rgba(0,0,0,0.25)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.1)'); gr.addColorStop(1, 'rgba(0,0,0,0.2)');
      g.fillStyle = gr; g.fillRect(i * bw, 0, bw, h);
    }
    for (let y = 0; y < h; y += h / 4) { g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(0, y, w, 3); }
  }),
  birch: canvasTex(128, (g, w, h) => {
    g.fillStyle = '#ecebe6'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(20,20,20,${rr(0.4, 0.9)})`; g.fillRect(rnd() * w, rnd() * h, rr(6, 30), rr(1, 4)); }
  }),
  bark: canvasTex(128, (g, w, h) => {
    g.fillStyle = '#5a4634'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 60; i++) { g.fillStyle = hsl(25, 25, rr(15, 35), 0.6); g.fillRect(rnd() * w, 0, rr(1, 4), h); }
  }),
  net: canvasTex(64, (g, w, h) => {
    g.clearRect(0, 0, w, h); g.fillStyle = '#f4f4f4';
    for (let i = 0; i < w; i += 8) { g.fillRect(i, 0, 1, h); g.fillRect(0, i, w, 1); }
  }),
};
// карта нормалей ряби для воды
T.waterN = (() => {
  const n = 256, c = document.createElement('canvas'); c.width = c.height = n;
  const g = c.getContext('2d'), img = g.createImageData(n, n);
  const waves = Array.from({ length: 7 }, () => ({ kx: Math.round(rr(-6, 6)), ky: Math.round(rr(-6, 6)) || 1, a: rr(0.3, 1), p: rr(0, 6.28) }));
  const hgt = (x, y) => waves.reduce((s, w) => s + w.a * Math.sin(2 * Math.PI * (w.kx * x + w.ky * y) / n + w.p), 0);
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const dx = hgt(x + 1, y) - hgt(x - 1, y), dy = hgt(x, y + 1) - hgt(x, y - 1);
    const v = new THREE.Vector3(-dx * 2, -dy * 2, 1).normalize(); const i = (y * n + x) * 4;
    img.data[i] = (v.x * 0.5 + 0.5) * 255; img.data[i + 1] = (v.y * 0.5 + 0.5) * 255; img.data[i + 2] = (v.z * 0.5 + 0.5) * 255; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
})();
T.blob = canvasTex(128, (g, w, h) => { const gr = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2); gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(0.6, 'rgba(0,0,0,0.7)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }, { srgb: false });
function rep(tex, rx, ry = rx) { const t = tex.clone(); t.needsUpdate = true; t.repeat.set(rx, ry); return t; }

// ---------- материалы ----------
const M = {
  lawn: new THREE.MeshStandardMaterial({ map: rep(T.lawn, 1 / 2.4), aoMap: rep(T.macro, 1 / 18), aoMapIntensity: 0.9, roughness: 1 }),
  meadow: new THREE.MeshStandardMaterial({ map: rep(T.meadow, 1 / 3.5), aoMap: rep(T.macro, 1 / 40), aoMapIntensity: 1, roughness: 1 }),
  wetMeadow: new THREE.MeshStandardMaterial({ map: rep(T.meadow, 1 / 3), color: 0x92a06a, roughness: 1 }),
  deck: new THREE.MeshStandardMaterial({ map: T.deck, roughness: 0.8 }),
  clad: new THREE.MeshStandardMaterial({ map: T.clad, roughness: 0.75, metalness: 0.05 }),
  slats: new THREE.MeshStandardMaterial({ map: T.slats, roughness: 0.75 }),
  plinth: new THREE.MeshStandardMaterial({ color: 0x2a2c2f, roughness: 0.8 }),
  fascia: new THREE.MeshStandardMaterial({ color: 0x26282b, roughness: 0.55, metalness: 0.3 }),
  roof: new THREE.MeshStandardMaterial({ map: rep(T.roofMembrane, 1 / 2), roughness: 0.9 }),
  frame: new THREE.MeshStandardMaterial({ color: 0x1c1d1f, roughness: 0.45, metalness: 0.4 }),
  sill: new THREE.MeshStandardMaterial({ color: 0x9a9da0, roughness: 0.4, metalness: 0.6 }),
  glass: new THREE.MeshPhysicalMaterial({ color: 0x141d25, roughness: 0.03, metalness: 0.15, envMapIntensity: 1.1, clearcoat: 1, clearcoatRoughness: 0.02, transparent: true, opacity: 0.72, depthWrite: false }),
  curtain: new THREE.MeshStandardMaterial({ color: 0xd9d2c3, roughness: 0.95 }),
  interior: new THREE.MeshStandardMaterial({ color: 0x0d1013, roughness: 1 }),
  steelDoor: new THREE.MeshStandardMaterial({ color: 0x2b2e31, roughness: 0.45, metalness: 0.5 }),
  door: new THREE.MeshStandardMaterial({ map: rep(T.slats, 1, 1), roughness: 0.6 }),
  pavers: new THREE.MeshStandardMaterial({ map: T.pavers, roughness: 0.9 }),
  asphalt: new THREE.MeshStandardMaterial({ map: rep(T.asphalt, 1 / 10), aoMap: rep(T.macro, 1 / 35), aoMapIntensity: 0.6, roughness: 0.95 }),
  gravel: new THREE.MeshStandardMaterial({ map: rep(T.gravel, 1 / 1.5), roughness: 1 }),
  stone: new THREE.MeshStandardMaterial({ map: T.stone, roughness: 0.7 }),
  tiles: new THREE.MeshStandardMaterial({ map: T.tiles, roughness: 0.3, side: THREE.BackSide }),
  water: new THREE.MeshPhysicalMaterial({ color: 0x0b86a8, roughness: 0.03, metalness: 0, transparent: true, opacity: 0.8,
    normalMap: rep(T.waterN, 0.35), normalScale: new THREE.Vector2(0.3, 0.3), envMapIntensity: 0.55, specularIntensity: 0.6 }),
  streamWater: new THREE.MeshPhysicalMaterial({ color: 0x24362c, roughness: 0.08, normalMap: rep(T.waterN, 0.3), normalScale: new THREE.Vector2(0.25, 0.25), envMapIntensity: 0.45 }),
  rubber: new THREE.MeshStandardMaterial({ map: rep(T.rubber, 1 / 1.5), roughness: 0.95 }),
  line: new THREE.MeshStandardMaterial({ color: 0xf2f2ee, roughness: 0.8 }),
  sand: new THREE.MeshStandardMaterial({ map: rep(T.sand, 1 / 1), roughness: 1 }),
  wood: new THREE.MeshStandardMaterial({ map: rep(T.slats, 0.6, 0.6), roughness: 0.7 }),
  steel: new THREE.MeshStandardMaterial({ color: 0x8b8f93, roughness: 0.35, metalness: 0.85 }),
  black: new THREE.MeshStandardMaterial({ color: 0x18191b, roughness: 0.5, metalness: 0.4 }),
  meshFence: new THREE.MeshStandardMaterial({ map: T.mesh, alphaTest: 0.4, side: THREE.DoubleSide, roughness: 0.6, metalness: 0.3 }),
  ranch: new THREE.MeshStandardMaterial({ map: T.ranch, alphaTest: 0.4, side: THREE.DoubleSide, roughness: 0.5, metalness: 0.45 }),
  post: new THREE.MeshStandardMaterial({ color: 0x2b2d30, roughness: 0.5, metalness: 0.5 }),
  net: new THREE.MeshStandardMaterial({ map: rep(T.net, 6, 1.2), alphaTest: 0.3, side: THREE.DoubleSide, transparent: true }),
  birch: new THREE.MeshStandardMaterial({ map: rep(T.birch, 1, 3), roughness: 0.9 }),
  bark: new THREE.MeshStandardMaterial({ map: rep(T.bark, 1, 2), roughness: 1 }),
  pole: new THREE.MeshStandardMaterial({ color: 0x7c7466, roughness: 1 }),
  cushion: new THREE.MeshStandardMaterial({ color: 0xe8e2d6, roughness: 1 }),
  umbrella: new THREE.MeshStandardMaterial({ color: 0xe9e0cc, roughness: 1, side: THREE.DoubleSide }),
};

// ---------- геометрические помощники ----------
function worldUV(geo, scale = 1) {                // UV в метрах — текстуры не растягиваются
  const p = geo.attributes.position, n = geo.attributes.normal, uv = geo.attributes.uv;
  for (let i = 0; i < p.count; i++) {
    const ax = Math.abs(n.getX(i)), ay = Math.abs(n.getY(i)), az = Math.abs(n.getZ(i));
    let u, v;
    if (ay >= ax && ay >= az) { u = p.getX(i); v = p.getZ(i); }
    else if (ax >= az) { u = p.getZ(i); v = p.getY(i); }
    else { u = p.getX(i); v = p.getY(i); }
    uv.setXY(i, u / scale, v / scale);
  }
  uv.needsUpdate = true; return geo;
}
function add(mesh, cast = true, recv = true) { mesh.castShadow = cast; mesh.receiveShadow = recv; scene.add(mesh); return mesh; }
// коробка по плановым координатам: x0..x1 (восток), y0..y1 (север), h0..h1 (высота)
function boxP(x0, y0, x1, y1, h0, h1, mat, uvScale = 1) {
  const w = Math.abs(x1 - x0), d = Math.abs(y1 - y0), h = h1 - h0;
  const g = new THREE.BoxGeometry(w, h, d);
  g.translate(X((x0 + x1) / 2), (h0 + h1) / 2, Z((y0 + y1) / 2));
  worldUV(g, uvScale);
  return add(new THREE.Mesh(g, mat));
}
function boxL(lx0, ly0, lx1, ly1, h0, h1, mat, uvScale = 1) {
  const a = L(lx0, ly0), b = L(lx1, ly1);
  return boxP(Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1]), h0, h1, mat, uvScale);
}
function flatShape(pts, holes = [], h = 0, mat) {   // плоский многоугольник по плановым точкам
  const sh = new THREE.Shape(pts.map(p => new THREE.Vector2(X(p[0]), -Z(p[1]))));
  holes.forEach(hp => sh.holes.push(new THREE.Path(hp.map(p => new THREE.Vector2(X(p[0]), -Z(p[1]))))));
  const g = new THREE.ShapeGeometry(sh); g.rotateX(-Math.PI / 2); g.translate(0, h, 0);
  return add(new THREE.Mesh(g, mat), false, true);
}
function segBox(p, q, h0, h1, thick, mat, uvScale = 1) {  // стенка/забор между двумя плановыми точками
  const a = V(p[0], p[1]), b = V(q[0], q[1]);
  const len = a.distanceTo(b), g = new THREE.BoxGeometry(len, h1 - h0, thick);
  worldUV(g, uvScale);
  const m = new THREE.Mesh(g, mat);
  m.position.set((a.x + b.x) / 2, (h0 + h1) / 2, (a.z + b.z) / 2);
  m.rotation.y = -Math.atan2(b.z - a.z, b.x - a.x);
  return add(m);
}
function cyl(x, y, h0, h1, r, mat, seg = 16) {
  const g = new THREE.CylinderGeometry(r, r, h1 - h0, seg);
  const m = new THREE.Mesh(g, mat); m.position.set(X(x), (h0 + h1) / 2, Z(y)); return add(m);
}

// листва — инстансы «карточек» с листьями + тёмное ядро, чтобы крона не просвечивала насквозь
const leafMats = {};
function leafMat(kind, tint) {
  const key = kind + '|' + new THREE.Color(tint).getHexString();
  if (!leafMats[key]) { leafMats[key] = new THREE.MeshStandardMaterial({ map: T[kind], color: new THREE.Color(tint), alphaTest: 0.3, alphaToCoverage: !HQ, side: THREE.DoubleSide, roughness: 0.9 });
    leafMats[key].onBeforeCompile = sh => { sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_begin>', '#include <normal_fragment_begin>\n\tnormal = normalize( vNormal );'); }; }
  return leafMats[key];
}
const leafGeo = new THREE.PlaneGeometry(1, 1);
function canopy(cxp, cyp, h, rx, ry, rz, n, size, { kind = 'leaf', tint = 0xffffff, core = 0x2e4a1e, droop = 0 } = {}) {
  const inst = new THREE.InstancedMesh(leafGeo, leafMat(kind, tint), n);
  const d = new THREE.Object3D(), col = new THREE.Color(), c = V(cxp, cyp, h);
  for (let i = 0; i < n; i++) {
    const u = rr(-1, 1), th = rr(0, 6.28), sq = Math.sqrt(1 - u * u), rad = Math.pow(rnd(), 0.35);
    d.position.set(c.x + rx * sq * Math.cos(th) * rad, c.y + ry * u * rad - droop * rnd(), c.z + rz * sq * Math.sin(th) * rad);
    d.lookAt(2 * d.position.x - c.x, 2 * d.position.y - c.y, 2 * d.position.z - c.z); d.rotateZ(rr(0, 6.28)); d.rotateX(rr(-0.6, 0.6)); d.scale.setScalar(size * rr(0.7, 1.25));
    d.updateMatrix(); inst.setMatrixAt(i, d.matrix);
    col.setHSL(0, 0, rr(0.75, 1.1)); inst.setColorAt(i, col);
  }
  inst.castShadow = true; inst.receiveShadow = true; scene.add(inst);
  if (core) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 12), new THREE.MeshStandardMaterial({ color: core, roughness: 1 }));
    s.scale.set(rx * 0.55, ry * 0.55, rz * 0.55); s.position.copy(c); s.castShadow = true; s.receiveShadow = true; scene.add(s);
  }
}
function bush(px, py, r, h, color = 0x3f6b2a) {
  const tint = new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.55);
  canopy(px, py, h, r, r * 0.8, r, Math.round(90 * r * r + 40), 0.42, { tint, core: new THREE.Color(color).multiplyScalar(0.55) });
}
function thuja(px, py, hgt = 2.6) {
  const core = new THREE.Mesh(new THREE.ConeGeometry(0.42, hgt - 0.2, 12), new THREE.MeshStandardMaterial({ color: 0x1d3519, roughness: 1 }));
  core.position.copy(V(px, py, 0.1 + (hgt - 0.2) / 2)); add(core);
  const levels = 9;
  for (let i = 0; i < levels; i++) {
    const t = i / (levels - 1), r = 0.52 * (1 - t * 0.8) + 0.06;
    canopy(px, py, 0.3 + t * (hgt - 0.5), r, hgt / levels * 1.1, r, 45, 0.34, { kind: 'needle', tint: 0x9fbf8a, core: 0 });
  }
}
function tree(px, py, { h = 7, r = 2.6, birch = false, color = 0x4c7a2c, willow = false } = {}) {
  const trunkH = h * (willow ? 0.42 : birch ? 0.42 : 0.5), tw = 0.11 * h / 7 + 0.05;
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(tw * 0.7, tw * 1.25, trunkH + r * 0.6, 10), birch ? M.birch : M.bark);
  tr.position.copy(V(px, py, (trunkH + r * 0.6) / 2)); add(tr);
  for (let i = 0; i < 4; i++) {                    // ветви
    const br = new THREE.Mesh(new THREE.CylinderGeometry(tw * 0.25, tw * 0.45, r * 0.9, 6), M.bark);
    const a = i * 1.7 + rnd(); br.position.copy(V(px + Math.cos(a) * r * 0.25, py + Math.sin(a) * r * 0.25, trunkH + r * 0.15 + i * 0.3));
    br.rotation.set(-Math.sin(a) * 0.8, 0, -Math.cos(a) * 0.8); add(br);
  }
  const tint = new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.5);
  const kind = birch ? 'leafLight' : 'leaf';
  if (birch) {                                     // берёза: вытянутая плакучая крона ярусами
    for (let i = 0; i < 7; i++) {
      const a = rnd() * 6.28, d = i === 0 ? 0 : rr(0.2, 0.45) * r, cr = r * rr(0.45, 0.62);
      canopy(px + Math.cos(a) * d, py + Math.sin(a) * d, h * 0.32 + r * (0.3 + i * 0.35), cr, cr * 1.3, cr,
        Math.round(cr * cr * 140 + 80), 0.5, { kind, tint, core: 0, droop: r * 0.3 });
    }
    return;
  }
  const clusters = willow ? 6 : 5;
  for (let i = 0; i < clusters; i++) {
    const a = rnd() * 6.28, d = i === 0 ? 0 : rr(0.35, 0.6) * r;
    const cr = r * (i === 0 ? 0.75 : rr(0.45, 0.6));
    canopy(px + Math.cos(a) * d, py + Math.sin(a) * d, trunkH + r * (i === 0 ? 0.75 : rr(0.4, 1.0)), cr, cr * (willow ? 1.2 : 0.85), cr,
      Math.round(cr * cr * 70 + 60), birch ? 0.5 : 0.6, { kind, tint, core: new THREE.Color(color).multiplyScalar(0.3), droop: willow ? r * 0.5 : 0 });
  }
}

// ---------- земля, газон, улица, ручей ----------
const P = S.plot;
const B = S.road.B, C = S.road.C;
const rd = [C[0] - B[0], C[1] - B[1]], rlen = Math.hypot(...rd), ru = [rd[0] / rlen, rd[1] / rlen];
const re = [ru[1], -ru[0]];                                   // нормаль на восток (к улице)
const along = (p, s, e) => [p[0] + ru[0] * s + re[0] * e, p[1] + ru[1] * s + re[1] * e];
const BIG = 420;
const pool = S.leisure.pool;                                   // [lx0, ly0, lx1, ly1]
const poolP = [L(pool[0], pool[1]), L(pool[2], pool[1]), L(pool[2], pool[3]), L(pool[0], pool[3])];
{
  // общий луг без щели по контуру участка; отверстие только под чашу бассейна
  const outer = [[cx - BIG, cy - BIG], [cx + BIG, cy - BIG], [cx + BIG, cy + BIG], [cx - BIG, cy + BIG]];
  flatShape(outer, [poolP.slice().reverse()], -0.03, M.meadow);
}
flatShape(P, [poolP.slice().reverse()], 0, M.lawn);

// улица 1905 года: обочина, асфальт 5.5 м, обочина
function band(e0, e1, s0, s1, h, mat) {
  flatShape([along(B, s0, e0), along(B, s1, e0), along(B, s1, e1), along(B, s0, e1)], [], h, mat);
}
band(1.6, 2.4, -120, 140, 0.005, M.gravel);
band(2.4, 7.9, -120, 140, 0.012, M.asphalt);
band(7.9, 8.7, -120, 140, 0.005, M.gravel);
// съезд к парковке
const pk = S.parking;
flatShape([[pk[1][0], pk[1][1]], along([pk[1][0], pk[1][1]], 0, 2.5).map((v, i) => v), along([pk[2][0], pk[2][1]], 0, 2.5), [pk[2][0], pk[2][1]]], [], 0.02, M.pavers);

// ручей к западу от участка (по карте ≈10–20 м)
const STREAM = [[-20, -60], [-15, -25], [-12, -2], [-10.5, 12], [-8, 30], [-5, 60]];   // ≈10 м от SW угла, ≈17 м от NW
function ribbon(pts, w, h, mat) {
  const left = [], right = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy), nx = -dy / l, ny = dx / l;
    left.push([pts[i][0] + nx * w / 2, pts[i][1] + ny * w / 2]); right.push([pts[i][0] - nx * w / 2, pts[i][1] - ny * w / 2]);
  }
  return flatShape(left.concat(right.reverse()), [], h, mat);
}
ribbon(STREAM, 6.5, -0.01, M.wetMeadow);
ribbon(STREAM, 1.5, 0.004, M.streamWater);

// ---------- дом DP-Module «Модерн»: 7 модулей, плоская кровля ----------
const FL = 0.55, WALL_TOP = 3.25, ROOF_TOP = 3.5;   // кровельный пирог ~25 см
// цоколь (на сваях, зашит панелями)
S.house.blocks.forEach(b => boxL(b[0] + 0.06, b[1] + 0.06, b[2] - 0.06, b[3] - 0.06, 0, FL, M.plinth));
// стены: основной объём — графит, мастер-модуль — термодерево
boxL(0, 0, 14, 7.5, FL, WALL_TOP, M.clad, 1);
boxL(0, 7.5, 7, 10, FL, WALL_TOP, M.slats, 1);
// деревянные порталы у входа и у выхода в сад (в пределах одного модуля 2.5 м)
boxL(14, 2.75, 14.04, 4.85, FL, WALL_TOP, M.slats, 1);
boxL(-0.04, 3.7, 0, 4.98, FL, WALL_TOP, M.slats, 1);
// нащельники на стыках модулей
[2.5, 5.0].forEach(j => { boxL(-0.015, j - 0.025, 0, j + 0.025, FL, WALL_TOP, M.fascia); boxL(14, j - 0.025, 14.015, j + 0.025, FL, WALL_TOP, M.fascia); });
boxL(6.975, -0.015, 7.025, 0, FL, WALL_TOP, M.fascia); boxL(6.975, 7.5, 7.025, 7.515, FL, WALL_TOP, M.fascia);
// кровля с небольшим выносом и тонким карнизом
const OV = 0.28;
boxL(-OV, -OV, 14 + OV, 7.5 + OV, WALL_TOP, ROOF_TOP, M.fascia);
boxL(-OV, 7.5, 7 + OV, 10 + OV, WALL_TOP, ROOF_TOP, M.fascia);
boxL(-OV + 0.12, -OV + 0.12, 14 + OV - 0.12, 7.5 + OV - 0.12, ROOF_TOP, ROOF_TOP + 0.02, M.roof, 2);
boxL(-OV + 0.12, 7.5, 7 + OV - 0.12, 10 + OV - 0.12, ROOF_TOP, ROOF_TOP + 0.02, M.roof, 2);
// козырёк над входом (консоль 1.7 м) с подшивкой из термодерева
boxL(14, 2.4, 15.7, 5.2, WALL_TOP + 0.05, ROOF_TOP - 0.05, M.fascia);
boxL(14, 2.45, 15.65, 5.15, WALL_TOP + 0.02, WALL_TOP + 0.05, M.slats, 1);
// вентвыходы
[[3, 3], [10.5, 5], [5, 8.8]].forEach(([a, b]) => { const p = L(a, b); cyl(p[0], p[1], ROOF_TOP, ROOF_TOP + 0.45, 0.07, M.black, 12); });
// уклон кровли на север: наружные желоба по северным свесам, две водосточные трубы с отводом и лотками
boxL(7, 7.5 + OV, 14 + OV, 7.5 + OV + 0.13, WALL_TOP - 0.06, WALL_TOP + 0.06, M.fascia);
boxL(-OV, 10 + OV, 7 + OV, 10 + OV + 0.13, WALL_TOP - 0.06, WALL_TOP + 0.06, M.fascia);
[[13.7, 7.5], [0.3, 10.0]].forEach(([a, b]) => {
  const p = L(a, b + 0.14);
  cyl(p[0], p[1], 0.25, WALL_TOP - 0.05, 0.045, M.fascia, 10);
  const q = L(a, b + OV + 0.06); boxP(Math.min(p[0], q[0]) - 0.04, Math.min(p[1], q[1]), Math.max(p[0], q[0]) + 0.04, Math.max(p[1], q[1]), WALL_TOP - 0.12, WALL_TOP - 0.04, M.fascia);
  boxP(p[0] - 0.045, p[1], p[0] + 0.045, p[1] + 0.32, 0.12, 0.22, M.fascia);          // отвод от стены
  boxP(p[0] - 0.14, p[1] + 0.3, p[0] + 0.14, p[1] + 0.8, 0, 0.04, M.stone, 0.6);      // лоток
});
// наружные блоки кондиционеров на кронштейнах
[[9.0, 7.5, 1], [6.6, 0, -1]].forEach(([a, b, s]) => {
  const p0 = L(a - 0.4, b), p1 = L(a + 0.4, b + s * 0.3);
  const unit = boxP(Math.min(p0[0], p1[0]), Math.min(p0[1], p1[1]), Math.max(p0[0], p1[0]), Math.max(p0[1], p1[1]), 0.65, 1.2, new THREE.MeshStandardMaterial({ color: 0xe6e6e3, roughness: 0.5 }));
  const g = L(a, b + s * 0.302); const grille = new THREE.Mesh(new THREE.CircleGeometry(0.2, 24), M.black);
  grille.position.copy(V(g[0] - 0.12, g[1], 0.92)); grille.rotation.y = s > 0 ? Math.PI : 0; add(grille);
  void unit;
  [a - 0.3, a + 0.3].forEach(x => { const k0 = L(x - 0.02, b), k1 = L(x + 0.02, b + s * 0.34); boxP(Math.min(k0[0], k1[0]), Math.min(k0[1], k1[1]), Math.max(k0[0], k1[0]), Math.max(k0[1], k1[1]), 0.6, 0.65, M.black); });
});

// окна и двери: стена, центр вдоль стены (лок. м), ширина, низ проёма от пола, высота
const WALLS = {
  S: { at: a => L(a, 0), n: [0, -1] }, N: { at: a => L(a, 7.5), n: [0, 1] }, NX: { at: a => L(a, 10), n: [0, 1] },
  E: { at: a => L(14, a), n: [1, 0] }, NE: { at: a => L(7, a), n: [1, 0] }, W: { at: a => L(0, a), n: [-1, 0] },
};
const WIN = [
  { w: 'S', a: 1.8, wd: 1.4, sill: 0.9, h: 1.5 },                 // спальня
  { w: 'S', a: 5.3, wd: 1.4, sill: 0.9, h: 1.5 },                 // детская
  { w: 'S', a: 8.6, wd: 1.6, sill: 1.1, h: 1.0 },                 // кухня над столешницей
  { w: 'S', a: 11.8, wd: 3.2, sill: 0.05, h: 2.35, pano: true },  // столовая — панорама на юг
  { w: 'E', a: 1.4, wd: 1.6, sill: 0.05, h: 2.35, pano: true },   // кухня-столовая на восток
  { w: 'E', a: 3.8, wd: 1.0, sill: 0, h: 2.3, entry: true, off: 0.045 }, // входная дверь (стальная, антрацит)
  { w: 'E', a: 6.25, wd: 2.0, sill: 0, h: 2.35, pano: true },     // гостиная → терраса
  { w: 'N', a: 8.25, wd: 0.7, sill: 1.6, h: 0.6 },                // санузел
  { w: 'N', a: 11.75, wd: 2.2, sill: 0.6, h: 1.7 },               // гостиная на север
  { w: 'NE', a: 8.75, wd: 0.6, sill: 1.6, h: 0.6 },               // с/у мастер
  { w: 'NX', a: 1.8, wd: 1.2, sill: 1.0, h: 1.4 },                // мастер-спальня (север, шумоизоляция)
  { w: 'NX', a: 5.3, wd: 0.8, sill: 1.6, h: 0.6 },                // с/у мастер
  { w: 'W', a: 1.25, wd: 1.4, sill: 0.9, h: 1.5 },                // спальня в сад
  { w: 'W', a: 4.5, wd: 0.9, sill: 0, h: 2.3, pano: true, off: 0.045 }, // коридор → сад (стеклянная дверь)
  { w: 'W', a: 8.75, wd: 2.0, sill: 0, h: 2.35, pano: true },     // мастер → терраса (в деревянном модуле)
];
function windowAt(spec) {
  const W = WALLS[spec.w], c = W.at(spec.a), n = W.n, t = [-n[1], n[0]];
  const base = FL + spec.sill, top = base + spec.h, mid = (base + top) / 2;
  const grp = new THREE.Group();
  const o = spec.off || 0;                          // локальная +Z — наружная нормаль стены
  grp.position.copy(V(c[0] + n[0] * o, c[1] + n[1] * o, 0)); grp.rotation.y = Math.atan2(n[0], -n[1]);
  const mk = (geo, mat, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; grp.add(m); return m; };
  const fw = 0.07;
  if (spec.entry) {
    mk(new THREE.BoxGeometry(spec.wd, spec.h, 0.06), M.steelDoor, 0, mid, 0.03);
    mk(new THREE.BoxGeometry(0.035, 1.3, 0.04), M.steel, spec.wd / 2 - 0.14, base + 1.1, 0.1);
    mk(new THREE.BoxGeometry(0.03, 0.07, 0.03), M.steel, spec.wd / 2 - 0.14, base + 0.88, 0.075);   // замок
    mk(new THREE.BoxGeometry(spec.wd + 0.16, 0.08, 0.1), M.frame, 0, top + 0.04, 0.05);
    mk(new THREE.BoxGeometry(0.08, spec.h, 0.1), M.frame, -spec.wd / 2 - 0.04, mid, 0.05);
    mk(new THREE.BoxGeometry(0.08, spec.h, 0.1), M.frame, spec.wd / 2 + 0.04, mid, 0.05);
  } else {
    // тёмная «глубина комнаты», штора и полупрозрачное стекло перед ними
    mk(new THREE.BoxGeometry(spec.wd - 0.04, spec.h - 0.04, 0.004), M.interior, 0, mid, 0.003);
    if (!spec.pano || spec.wd < 2.1) mk(new THREE.BoxGeometry(spec.wd * 0.28, spec.h - 0.1, 0.004), M.curtain, -spec.wd * 0.33, mid, 0.008);
    const gl = mk(new THREE.BoxGeometry(spec.wd - 0.04, spec.h - 0.04, 0.01), M.glass, 0, mid, 0.022); gl.castShadow = false;
    mk(new THREE.BoxGeometry(spec.wd + 0.02, fw, 0.1), M.frame, 0, top, 0.05);
    mk(new THREE.BoxGeometry(spec.wd + 0.02, fw, 0.1), M.frame, 0, base, 0.05);
    mk(new THREE.BoxGeometry(fw, spec.h, 0.1), M.frame, -spec.wd / 2, mid, 0.05);
    mk(new THREE.BoxGeometry(fw, spec.h, 0.1), M.frame, spec.wd / 2, mid, 0.05);
    const parts = spec.pano ? Math.max(1, Math.round(spec.wd / 1.2)) : (spec.wd > 1 ? 2 : 1);
    for (let i = 1; i < parts; i++) mk(new THREE.BoxGeometry(0.05, spec.h, 0.08), M.frame, -spec.wd / 2 + spec.wd * i / parts, mid, 0.05);
    if (spec.pano) {                                 // графитовая рамка-наличник у панорамных окон
      const d = 0.16, th = 0.06;
      mk(new THREE.BoxGeometry(spec.wd + 2 * th, th, d), M.fascia, 0, top + th / 2, d / 2);
      mk(new THREE.BoxGeometry(th, spec.h + th, d), M.fascia, -spec.wd / 2 - th / 2, mid, d / 2);
      mk(new THREE.BoxGeometry(th, spec.h + th, d), M.fascia, spec.wd / 2 + th / 2, mid, d / 2);
    } else {                                         // откос-рамка и отлив: стекло читается утопленным
      const d = 0.12, th = 0.04;
      mk(new THREE.BoxGeometry(spec.wd + 2 * th, th, d), M.fascia, 0, top + th / 2, d / 2);
      mk(new THREE.BoxGeometry(th, spec.h + th, d), M.fascia, -spec.wd / 2 - th / 2, mid, d / 2);
      mk(new THREE.BoxGeometry(th, spec.h + th, d), M.fascia, spec.wd / 2 + th / 2, mid, d / 2);
      mk(new THREE.BoxGeometry(spec.wd + 0.12, 0.03, 0.17), M.sill, 0, base - 0.02, 0.085);
    }
  }
  scene.add(grp);
}
WIN.forEach(windowAt);
// настенные светильники у дверей
[['E', 3.0], ['E', 4.6], ['W', 3.85]].forEach(([w, a]) => {
  const W = WALLS[w], c = W.at(a); const p = [c[0] + W.n[0] * 0.06, c[1] + W.n[1] * 0.06];
  boxP(p[0] - 0.05, p[1] - 0.05, p[0] + 0.05, p[1] + 0.05, FL + 2.0, FL + 2.25, M.black);
});

// ---------- террасы (лиственница) со ступенями ----------
const DECK = FL - 0.05;
S.terraces.forEach(([name, a, b, c, d]) => {
  boxL(a, b, c, d, 0, DECK, M.deck, 1);
});
const rt = S.terraces[0], gt = S.terraces[1];
for (let i = 1; i <= 2; i++) {                    // лестницы: 3 подступенка по ~170 мм, проступь 300 мм
  boxL(rt[3], 2.5, rt[3] + 0.3 * (3 - i), 4.3, 0, DECK * i / 3, M.deck, 1);            // к калитке
  boxL(gt[1] - 0.3 * (3 - i), 0, gt[1], 1.15, 0, DECK * i / 3, M.deck, 1);             // на газон
}
// стол и стулья на садовой террасе
{
  const tc = L(-1.0, 9.25);
  boxP(tc[0] - 0.42, tc[1] - 0.6, tc[0] + 0.42, tc[1] + 0.6, DECK + 0.72, DECK + 0.76, M.wood);
  [[-0.35, -0.5], [0.35, -0.5], [-0.35, 0.5], [0.35, 0.5]].forEach(([a, b]) => cyl(tc[0] + a, tc[1] + b, DECK, DECK + 0.72, 0.025, M.black, 8));
  [[-0.75, -0.3], [-0.75, 0.35]].forEach(([a, b]) => {
    boxP(tc[0] + a - 0.22, tc[1] + b - 0.22, tc[0] + a + 0.22, tc[1] + b + 0.22, DECK + 0.42, DECK + 0.46, M.black);
    boxP(tc[0] + a - 0.24, tc[1] + b - 0.22, tc[0] + a - 0.2, tc[1] + b + 0.22, DECK + 0.46, DECK + 0.9, M.black);
  });
}
// кашпо с растениями у входа
[[14.9, 0.4], [15.2, 7.1]].forEach(([a, b]) => {
  const p = L(a, b); boxP(p[0] - 0.25, p[1] - 0.25, p[0] + 0.25, p[1] + 0.25, DECK, DECK + 0.6, M.fascia);
  bush(p[0], p[1], 0.38, DECK + 0.75, 0x4f7a32);
});

// ---------- парковка, машины, дорожка ----------
boxP(pk[0][0], pk[0][1], pk[1][0], pk[2][1], 0, 0.05, M.pavers, 1);
const path = S.leisure.path;
boxL(path[0], path[1], path[2], path[3], 0, 0.04, M.pavers, 1);
function car(px, py, color, headingDeg) {
  const g = new THREE.Group();
  const body = new THREE.MeshPhysicalMaterial({ color, metalness: 0.0, roughness: 0.35, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 0.55 });
  const glassC = new THREE.MeshPhysicalMaterial({ color: 0x11161b, roughness: 0.05, metalness: 0.2, clearcoat: 1, envMapIntensity: 0.5 });
  const m = (geo, mat, x, y, z) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; g.add(o); return o; };
  // силуэт кроссовера сбоку (нос — к −X), выдавлен по ширине со скруглением
  const prof = [[-2.3, 0.38], [-2.32, 0.72], [-2.18, 0.86], [-1.3, 0.98], [-0.85, 1.04], [-0.2, 1.52], [1.35, 1.54], [1.95, 1.18],
    [2.28, 1.08], [2.32, 0.72], [2.26, 0.38]];
  const ext = (pts, depth, bev) => {
    const sh = new THREE.Shape(pts.map(p => new THREE.Vector2(p[0], p[1])));
    const geo = new THREE.ExtrudeGeometry(sh, { depth, bevelEnabled: true, bevelThickness: bev, bevelSize: bev, bevelSegments: 3, curveSegments: 6 });
    geo.translate(0, 0, -depth / 2); return geo;
  };
  m(ext(prof, 1.62, 0.1), body, 0, 0, 0);
  // остекление: боковые окна и лобовое — чуть шире кузова
  m(ext([[-0.95, 1.02], [-0.3, 1.56], [1.38, 1.58], [2.05, 1.19], [2.12, 1.02]], 1.76, 0.06), glassC, 0, 0, 0);
  m(ext([[-0.2, 1.53], [1.33, 1.55], [1.3, 1.6], [-0.15, 1.59]], 1.5, 0.05), body, 0, 0, 0);   // крыша
  const tire = new THREE.CylinderGeometry(0.36, 0.36, 0.26, 28); tire.rotateX(Math.PI / 2);
  const rim = new THREE.CylinderGeometry(0.23, 0.23, 0.27, 18); rim.rotateX(Math.PI / 2);
  const rubberM = new THREE.MeshStandardMaterial({ color: 0x141414, roughness: 0.9 });
  const archM = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.8 });
  [[-1.42, 0.8], [1.42, 0.8], [-1.42, -0.8], [1.42, -0.8]].forEach(([x, z]) => {
    m(tire, rubberM, x, 0.36, z); m(rim, M.steel, x, 0.36, z);
    const arch = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.05, 6, 16, Math.PI), archM); arch.position.set(x, 0.38, z * 1.12); g.add(arch);
  });
  const lamp = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff4dd, emissiveIntensity: 0.35 });
  const tail = new THREE.MeshStandardMaterial({ color: 0x8a0d0d, emissive: 0x3a0000 });
  [0.6, -0.6].forEach(z => { m(new THREE.BoxGeometry(0.08, 0.1, 0.42), lamp, -2.36, 0.8, z); m(new THREE.BoxGeometry(0.08, 0.12, 0.36), tail, 2.38, 0.92, z); });
  [0.93, -0.93].forEach(z => m(new THREE.BoxGeometry(0.2, 0.1, 0.14), body, -0.7, 1.12, z));   // зеркала
  m(new THREE.BoxGeometry(0.04, 0.13, 0.52), M.black, -2.42, 0.52, 0);          // номер
  m(new THREE.BoxGeometry(0.06, 0.18, 1.5), archM, -2.38, 0.42, 0);             // нижняя решётка/бампер
  m(new THREE.BoxGeometry(0.04, 0.12, 0.52), M.black, 2.42, 0.62, 0); m(new THREE.BoxGeometry(0.08, 0.2, 1.7), archM, 2.38, 0.45, 0);   // задний номер и бампер
  const sh = new THREE.Mesh(new THREE.PlaneGeometry(5.0, 2.2), new THREE.MeshBasicMaterial({ color: 0, map: T.blob, transparent: true, opacity: 0.75, depthWrite: false }));
  sh.rotation.x = -Math.PI / 2; sh.position.y = 0.056; g.add(sh);
  g.position.copy(V(px, py, 0)); g.rotation.y = THREE.MathUtils.degToRad(headingDeg);
  scene.add(g);
}
{
  const xm = (pk[0][0] + pk[1][0]) / 2 - 0.1, ym = (pk[0][1] + pk[2][1]) / 2, half = (pk[2][1] - pk[0][1]) / 4;
  car(xm, ym - half, 0xe9ebec, 0);
  car(xm + 0.15, ym + half, 0x1f3550, 0);
}

// ---------- бассейн ----------
{
  const [x0, y0] = L(pool[0], pool[1]), [x1, y1] = L(pool[2], pool[3]);
  const depth = 1.45, w = x1 - x0, d = y1 - y0;
  const g = new THREE.BoxGeometry(w, depth, d); g.translate(X((x0 + x1) / 2), -depth / 2, Z((y0 + y1) / 2));
  worldUV(g, 1);
  add(new THREE.Mesh(g, M.tiles), false, true);
  const wg = new THREE.PlaneGeometry(w, d); wg.rotateX(-Math.PI / 2); wg.translate(X((x0 + x1) / 2), -0.07, Z((y0 + y1) / 2));
  add(new THREE.Mesh(wg, M.water), false, true);
  const c = 0.4, top = 0.07;                       // бортик из светлого камня
  boxP(x0 - c, y0 - c, x1 + c, y0, 0, top, M.stone, 0.6); boxP(x0 - c, y1, x1 + c, y1 + c, 0, top, M.stone, 0.6);
  boxP(x0 - c, y0, x0, y1, 0, top, M.stone, 0.6); boxP(x1, y0, x1 + c, y1, 0, top, M.stone, 0.6);
  // поручень-лестница
  const lp = [x1 - 0.05, y0 + 0.9];
  [0, 0.5].forEach(o => { cyl(lp[0], lp[1] + o, -0.6, 0.75, 0.025, M.steel, 10); });
  [0, 0.5].forEach(o => { const arc = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.025, 8, 16, Math.PI), M.steel); arc.position.copy(V(lp[0] + 0.2, lp[1] + o, 0.75)); add(arc); cyl(lp[0] + 0.4, lp[1] + o, 0.07, 0.75, 0.025, M.steel, 10); });
  // лежаки и зонт на газоне у бассейна
  [[-6.6, 2.9], [-6.6, 4.4]].forEach(([a, b]) => {
    const p = L(a, b);
    boxP(p[0] - 0.95, p[1] - 0.33, p[0] + 0.55, p[1] + 0.33, 0.25, 0.36, M.wood);
    boxP(p[0] - 0.95, p[1] - 0.3, p[0] + 0.5, p[1] + 0.3, 0.36, 0.42, M.cushion);
    const back = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.08, 0.62), M.cushion);
    back.position.copy(V(p[0] - 1.18, p[1], 0.62)); back.rotation.z = -0.8; add(back);
    [[-0.85, -0.28], [-0.85, 0.28], [0.45, -0.28], [0.45, 0.28]].forEach(([u, v]) => cyl(p[0] + u, p[1] + v, 0, 0.26, 0.03, M.black, 8));
  });
  const up = L(-6.7, 6.0);
  cyl(up[0], up[1], 0, 2.3, 0.025, M.steel, 8);
  const cone = new THREE.Mesh(new THREE.ConeGeometry(1.45, 0.45, 8, 1, true), M.umbrella);
  cone.position.copy(V(up[0], up[1], 2.25)); add(cone);
}

// ---------- банный чан / купель (дерево, печь с трубой) ----------
{
  const [tx, ty, tr] = S.leisure.tub, p = L(tx, ty);
  boxP(p[0] - tr - 0.3, p[1] - tr - 0.3, p[0] + tr + 0.3, p[1] + tr + 0.3, 0, 0.18, M.deck, 1);
  const staves = rep(T.slats, 6, 1); const tubM = new THREE.MeshStandardMaterial({ map: staves, roughness: 0.75, side: THREE.DoubleSide });
  const barrel = new THREE.Mesh(new THREE.CylinderGeometry(tr, tr * 0.97, 1.0, 40, 1, true), tubM);
  barrel.position.copy(V(p[0], p[1], 0.68)); add(barrel);
  const bottom = new THREE.Mesh(new THREE.CircleGeometry(tr, 40), M.wood); bottom.rotation.x = -Math.PI / 2; bottom.position.copy(V(p[0], p[1], 0.2)); add(bottom);
  [0.35, 1.0].forEach(h => { const band = new THREE.Mesh(new THREE.TorusGeometry(tr + 0.01, 0.018, 8, 48), M.black); band.rotation.x = Math.PI / 2; band.position.copy(V(p[0], p[1], h)); add(band); });
  const rim = new THREE.Mesh(new THREE.TorusGeometry(tr, 0.045, 8, 48), M.wood); rim.rotation.x = Math.PI / 2; rim.position.copy(V(p[0], p[1], 1.18)); add(rim);
  const wat = new THREE.Mesh(new THREE.CircleGeometry(tr - 0.03, 40), M.water); wat.rotation.x = -Math.PI / 2; wat.position.copy(V(p[0], p[1], 1.0)); add(wat, false, true);
  // печь снаружи и труба
  const sp = [p[0] - tr - 0.15, p[1] + 0.2];
  boxP(sp[0] - 0.22, sp[1] - 0.22, sp[0] + 0.22, sp[1] + 0.22, 0.18, 0.75, M.black);
  cyl(sp[0], sp[1], 0.75, 2.6, 0.06, M.steel, 12);
  // ступени к чану со стороны террасы
  boxP(p[0] + tr - 0.1, p[1] - 0.4, p[0] + tr + 0.35, p[1] + 0.4, 0.18, 0.55, M.deck, 1);
}

// ---------- спортплощадка ----------
{
  const sp = S.leisure.sport, [x0, y0] = L(sp[0], sp[1]), [x1, y1] = L(sp[2], sp[3]);
  boxP(x0, y0, x1, y1, 0, 0.04, M.rubber, 1);
  const lw = 0.05, ins = 0.3, h = 0.05;
  boxP(x0 + ins, y0 + ins, x1 - ins, y0 + ins + lw, 0.04, h, M.line); boxP(x0 + ins, y1 - ins - lw, x1 - ins, y1 - ins, 0.04, h, M.line);
  boxP(x0 + ins, y0 + ins, x0 + ins + lw, y1 - ins, 0.04, h, M.line); boxP(x1 - ins - lw, y0 + ins, x1 - ins, y1 - ins, 0.04, h, M.line);
  const xm = (x0 + x1) / 2;
  boxP(xm - lw / 2, y0 + ins, xm + lw / 2, y1 - ins, 0.04, h, M.line);
  cyl(xm, y0 + 0.15, 0, 1.6, 0.03, M.steel, 10); cyl(xm, y1 - 0.15, 0, 1.6, 0.03, M.steel, 10);
  const net = new THREE.Mesh(new THREE.PlaneGeometry(y1 - y0 - 0.3, 0.72), M.net);
  net.position.copy(V(xm, (y0 + y1) / 2, 1.2)); net.rotation.y = Math.PI / 2; add(net, false, false);
  boxP(xm - 0.01, y0 + 0.15, xm + 0.01, y1 - 0.15, 1.52, 1.56, M.line);
  // сетка-уловитель 2.5 м со стороны гостиной и парковки
  fenceRun([x0, y0 + 0.05], [x1, y0 + 0.05], 2.5, M.net, [0.6, 0.6], 2.6);
  fenceRun([x1 - 0.05, y0], [x1 - 0.05, y1], 2.5, M.net, [0.6, 0.6], 2.6);
  // турник в углу
  const tp = [x0 + 0.5, y1 - 0.5];
  cyl(tp[0], tp[1], 0, 2.45, 0.05, M.black, 12); cyl(tp[0] + 1.2, tp[1], 0, 2.45, 0.05, M.black, 12);
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 1.2, 8), M.steel); bar.rotation.z = Math.PI / 2; bar.position.copy(V(tp[0] + 0.6, tp[1], 2.3)); add(bar);
}

// ---------- детская зона: песочница и качели ----------
{
  const sd = S.leisure.sand, [x0, y0] = L(sd[0], sd[1]), [x1, y1] = L(sd[2], sd[3]);
  const t = 0.07, h = 0.3;
  boxP(x0, y0, x1, y0 + t, 0, h, M.wood); boxP(x0, y1 - t, x1, y1, 0, h, M.wood);
  boxP(x0, y0, x0 + t, y1, 0, h, M.wood); boxP(x1 - t, y0, x1, y1, 0, h, M.wood);
  boxP(x0 + t, y0 + t, x1 - t, y1 - t, 0, 0.2, M.sand, 1);
  const bucket = new THREE.MeshStandardMaterial({ color: 0xe0442a, roughness: 0.6 });
  cyl(x0 + 0.6, y0 + 0.7, 0.2, 0.38, 0.1, bucket, 14);
  const spade = new THREE.MeshStandardMaterial({ color: 0xf2c230, roughness: 0.6 });
  boxP(x1 - 0.7, y1 - 0.6, x1 - 0.3, y1 - 0.5, 0.2, 0.24, spade);
}
{
  const sw = S.leisure.swing, [x0, y0] = L(sw[0], sw[1]), [x1, y1] = L(sw[2], sw[3]);
  const ym = (y0 + y1) / 2, H = 2.2, beamH = H;
  const beam = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0 - 0.2, 0.12, 0.12), M.wood);
  beam.position.copy(V((x0 + x1) / 2, ym, beamH)); add(beam);
  [x0 + 0.15, x1 - 0.15].forEach(x => [-1, 1].forEach(s => {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, Math.hypot(H, 0.75), 8), M.wood);
    leg.position.copy(V(x, ym + s * 0.375, H / 2)); leg.rotation.x = s * Math.atan2(0.75, H); add(leg);
  }));
  const seatM = new THREE.MeshStandardMaterial({ color: 0x2f7fc2, roughness: 0.6 });
  [x0 + (x1 - x0) * 0.33, x0 + (x1 - x0) * 0.67].forEach(x => {
    boxP(x - 0.22, ym - 0.12, x + 0.22, ym + 0.12, 0.42, 0.47, seatM);
    [-0.19, 0.19].forEach(o => cyl(x + o, ym, 0.47, beamH, 0.008, M.black, 6));
  });
}

// ---------- кусты, туи, деревья ----------
S.shrubs.forEach(([a, b, r]) => { const p = L(a, b); bush(p[0], p[1], r * 1.25, r * 0.8); });
// туи вдоль северного забора (приватность и шум от ж/д) и у западного
for (let x = 9.5; x < 23.5; x += 1.6) { if (x > 18.6) break; thuja(x, 15.3 + (x - 9.5) * -0.003); }
[[3.3, 4.9], [6.0, 11.0], [6.9, 13.0]].forEach(([x, y]) => thuja(x, y, 2.4));
// яблоня на заднем дворе (≥2 м от соседей)
tree(5.3, 3.4, { h: 4.0, r: 1.35, color: 0x4f7d2e });
// у ручья — ивы и берёзы, у соседей — деревья
tree(-14.5, -4, { h: 9, r: 3.6, willow: true, color: 0x6b8f3a }); tree(-7.5, 24, { h: 8, r: 3.2, willow: true, color: 0x6f9440 });
tree(-14, 10, { h: 13, r: 2.6, birch: true, color: 0x6d9a3a }); tree(-16, 15, { h: 12, r: 2.2, birch: true, color: 0x6a9638 });
tree(-14, -18, { h: 11, r: 3, color: 0x47702a }); tree(25, 33, { h: 10, r: 3.2, color: 0x4a742c });
tree(6, -10, { h: 8, r: 2.8, color: 0x527d30 }); tree(26, -9, { h: 7, r: 2.4, color: 0x4d772d });
tree(48, 34, { h: 11, r: 3.5, color: 0x45702a }); tree(52, -12, { h: 9, r: 3, birch: true, color: 0x6d9a3a });
function spruce(px, py, h = 18) {                  // ель — типичный для Одинцово хвойник
  cyl(px, py, 0, h * 0.95, 0.22, M.bark, 8);
  for (let i = 0; i < 8; i++) {
    const t = i / 7, r = 0.22 * h * (1 - t) + 0.4, y0 = 0.2 * h + t * 0.72 * h;
    const cone = new THREE.Mesh(new THREE.ConeGeometry(r, h * 0.22, 9), new THREE.MeshStandardMaterial({ color: 0x1f3a24, roughness: 1 }));
    cone.position.copy(V(px, py, y0)); add(cone);
    canopy(px, py, y0 - h * 0.03, r * 0.95, h * 0.08, r * 0.95, Math.round(r * r * 18 + 30), 0.9, { kind: 'needle', tint: 0x7fa070, core: 0 });
  }
}
[[-26, 22, 20], [-34, 6, 17], [58, 40, 22], [30, -40, 18], [-42, -22, 19], [70, -20, 16], [-24, -46, 21]].forEach(([x, y, h]) => spruce(x, y, h));
// камыш у ручья — куртинами, и прибрежные кусты
{
  const reedM = new THREE.MeshStandardMaterial({ color: 0x8c9a58, roughness: 1 });
  const geo = new THREE.ConeGeometry(0.025, 1.5, 4); geo.translate(0, 0.75, 0); const N = 1400; const inst = new THREE.InstancedMesh(geo, reedM, N);
  const dummy = new THREE.Object3D(), col = new THREE.Color(); let k = 0;
  while (k < N) {
    const i = Math.floor(rnd() * (STREAM.length - 1)), a = STREAM[i], b = STREAM[i + 1], t = rnd();
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy), side = rnd() < 0.5 ? -1 : 1, off = side * rr(0.6, 1.8);
    const qx = a[0] + dx * t + (-dy / l) * off, qy = a[1] + dy * t + (dx / l) * off, n = Math.floor(rr(12, 45));
    for (let j = 0; j < n && k < N; j++) {
      const r = rr(0, 0.7), th = rr(0, 6.28);
      dummy.position.copy(V(qx + Math.cos(th) * r, qy + Math.sin(th) * r, -0.02)); dummy.rotation.set(rr(-0.2, 0.2), 0, rr(-0.2, 0.2));
      dummy.scale.set(1, rr(0.5, 1.15), 1); dummy.updateMatrix(); inst.setMatrixAt(k, dummy.matrix);
      col.setHSL(rr(0.15, 0.22), rr(0.3, 0.45), rr(0.32, 0.48)); inst.setColorAt(k, col); k++;
    }
  }
  inst.castShadow = true; scene.add(inst);
  [[-15.5, -12], [-14, 3], [-12, 18], [-9.5, 40], [-18.5, -30]].forEach(([x, y]) => bush(x, y, rr(0.9, 1.4), 0.8, 0x56742f));
}

// ---------- заборы ----------
function fenceRun(p, q, height, mat, uvTile, postEvery = 2.5) {
  const len = Math.hypot(q[0] - p[0], q[1] - p[1]);
  const g = new THREE.PlaneGeometry(len, height);
  const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * len / uvTile[0], uv.getY(i) * height / uvTile[1]);
  const m = new THREE.Mesh(g, mat); const a = V(p[0], p[1]), b = V(q[0], q[1]);
  m.position.set((a.x + b.x) / 2, height / 2 + 0.05, (a.z + b.z) / 2); m.rotation.y = -Math.atan2(b.z - a.z, b.x - a.x);
  add(m, true, true);
  const n = Math.max(1, Math.round(len / postEvery));
  for (let i = 0; i <= n; i++) { const t = i / n; cyl(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, 0, height + 0.08, 0.035, M.post, 8); }
}
const [A_, B_, C_, D_] = P;
fenceRun(A_, B_, 1.53, M.meshFence, [0.4, 0.4]);    // соседи — 3D-сетка
fenceRun(C_, D_, 1.53, M.meshFence, [0.4, 0.4]);
fenceRun(D_, A_, 1.53, M.meshFence, [0.4, 0.4]);
// уличный забор-ранчо 1.8 м: проём под откатные ворота у парковки, калитка у дорожки
const fy = y => [B_[0] + (C_[0] - B_[0]) * (y - B_[1]) / (C_[1] - B_[1]), y];
const gateY0 = HY0 + path[1] - 0.05, gateY1 = HY0 + path[3] + 0.05;
fenceRun(fy(B_[1]), fy(gateY0), 1.8, M.ranch, [0.6, 0.6]);
fenceRun(fy(gateY1), fy(pk[0][1] - 0.1), 1.8, M.ranch, [0.6, 0.6]);
{
  const g0 = fy(gateY0), g1 = fy(gateY1);                 // калитка (дерево)
  segBox(g0, g1, 0.05, 1.85, 0.05, M.door, 1);
  cyl(...fy(pk[0][1] - 0.1), 0, 1.95, 0.06, M.post, 10); cyl(...fy(C_[1] - 0.05), 0, 1.95, 0.06, M.post, 10);
  [g0, g1].forEach(p => { cyl(p[0], p[1], 0, 1.95, 0.05, M.post, 10); boxP(p[0] - 0.07, p[1] - 0.07, p[0] + 0.07, p[1] + 0.07, 1.95, 2.1, M.black); });
  // адресная табличка, почтовый ящик, вызывная панель (на стороне улицы)
  const out = (p, e) => [p[0] + re[0] * e, p[1] + re[1] * e];
  const plateT = canvasTex(256, (g, w, h) => {
    g.fillStyle = '#1d4f91'; g.fillRect(0, 0, w, h); g.strokeStyle = '#fff'; g.lineWidth = 6; g.strokeRect(8, 8, w - 16, h - 16);
    g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = 'bold 34px sans-serif'; g.fillText('ул. 1905', w / 2, h * 0.45); g.fillText('года', w / 2, h * 0.78);
  }, { w: 256, h: 160 });
  const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.31), new THREE.MeshStandardMaterial({ map: plateT, roughness: 0.5 }));
  const pp = out(fy(gateY1 + 0.75), 0.06); plate.position.copy(V(pp[0], pp[1], 1.65)); plate.rotation.y = Math.atan2(re[0], -re[1]); add(plate);
  const mb = out(fy(gateY1 + 0.4), 0.05); boxP(mb[0] - 0.05, mb[1] - 0.16, mb[0] + 0.07, mb[1] + 0.16, 1.0, 1.38, M.fascia);
  const cp = out(g1, 0.06); boxP(cp[0] - 0.015, cp[1] - 0.04, cp[0] + 0.015, cp[1] + 0.04, 1.4, 1.55, M.black);
}
// откатные ворота: полотно-ранчо в раме, консольная балка, ролики; открыты только на ракурсе «Въезд»
const gateGroup = new THREE.Group(); scene.add(gateGroup);
{
  const a = fy(pk[0][1] - 0.05), b = fy(C_[1] - 0.1), inset = 0.12;
  const pa = [a[0] - re[0] * inset, a[1] - re[1] * inset], pb = [b[0] - re[0] * inset, b[1] - re[1] * inset];
  const len = Math.hypot(pb[0] - pa[0], pb[1] - pa[1]), H = 1.75;
  const leafG = new THREE.PlaneGeometry(len, H); const uv = leafG.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * len / 0.6, uv.getY(i) * H / 0.6);
  const A3 = V(pa[0], pa[1]), B3 = V(pb[0], pb[1]), rotY = -Math.atan2(B3.z - A3.z, B3.x - A3.x);
  const put = (geo, mat, along_, y) => { const m = new THREE.Mesh(geo, mat); const t = along_ / len;
    m.position.set(A3.x + (B3.x - A3.x) * t, y, A3.z + (B3.z - A3.z) * t); m.rotation.y = rotY; m.castShadow = m.receiveShadow = true; gateGroup.add(m); return m; };
  put(leafG, M.ranch, len / 2, 0.12 + H / 2);
  put(new THREE.BoxGeometry(len, 0.06, 0.04), M.post, len / 2, 0.12 + H);
  put(new THREE.BoxGeometry(len + 2.25, 0.1, 0.06), M.post, len / 2 - 1.1, 0.11);          // консольная балка
  put(new THREE.BoxGeometry(0.06, H, 0.04), M.post, 0, 0.12 + H / 2); put(new THREE.BoxGeometry(0.06, H, 0.04), M.post, len, 0.12 + H / 2);
  const gateLen = len;
  window.__gateShift = [-ru[0] * (gateLen + 0.1), -ru[1] * (gateLen + 0.1)];
}
function gateOpen(open) {
  const d = open ? window.__gateShift : [0, 0];
  gateGroup.position.set(d[0], 0, -d[1]);
  renderer.shadowMap.needsUpdate = true;
}

// ---------- соседи: дома, заборы из профлиста, опоры ЛЭП ----------
function neighborHouse(px, py, w, d, wallH, roofH, wallColor, roofColor, rot = 0, floors = 1) {
  const grp = new THREE.Group();
  const wm = new THREE.MeshStandardMaterial({ map: rep(T.siding, w / 1.1, wallH / 1.0), color: new THREE.Color(wallColor).multiplyScalar(0.78), roughness: 0.85 });
  const rt = rep(T.metalRoof, d / 1.2, 3); rt.rotation = Math.PI / 2;            // рёбра — вдоль ската
  const rm = new THREE.MeshStandardMaterial({ map: rt, color: roofColor, roughness: 0.55, metalness: 0.35, side: THREE.DoubleSide });
  const body = new THREE.Mesh(new THREE.BoxGeometry(w, wallH, d), wm); body.position.y = wallH / 2 + 0.4; grp.add(body);
  const base = new THREE.Mesh(new THREE.BoxGeometry(w + 0.1, 0.4, d + 0.1), new THREE.MeshStandardMaterial({ color: 0x8a847a, roughness: 1 })); base.position.y = 0.2; grp.add(base);
  const sh = new THREE.Shape([new THREE.Vector2(-w / 2, 0), new THREE.Vector2(w / 2, 0), new THREE.Vector2(0, roofH * (w / 2) / (w / 2 + 0.6) - 0.08)]);
  const gable = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: d, bevelEnabled: false }), wm);
  gable.position.set(0, wallH + 0.4, -d / 2); grp.add(gable);
  const slope = Math.hypot(w / 2 + 0.6, roofH), ang = Math.atan2(roofH, w / 2 + 0.6);
  [-1, 1].forEach(s => {
    const r = new THREE.Mesh(new THREE.BoxGeometry(slope, 0.06, d + 0.8), rm);
    r.position.set(s * (w / 4 + 0.15), wallH + 0.4 + roofH / 2 + 0.03, 0); r.rotation.z = -s * ang; grp.add(r);
  });
  const frameW = new THREE.MeshStandardMaterial({ color: 0xf4f4f0, roughness: 0.6 });
  for (let f = 0; f < floors; f++) for (let i = -1; i <= 1; i++) {
    [1, -1].forEach(s => {
      if (f === 0 && i === 0 && s === 1) return;      // здесь входная дверь
      const fr = new THREE.Mesh(new THREE.BoxGeometry(1.32, 1.42, 0.06), frameW); fr.position.set(i * w / 3.2, 1.75 + f * 2.8, s * (d / 2 + 0.02)); grp.add(fr);
      const wv = new THREE.Mesh(new THREE.BoxGeometry(1.18, 1.28, 0.07), M.glass); wv.position.set(i * w / 3.2, 1.75 + f * 2.8, s * (d / 2 + 0.03)); grp.add(wv);
      const mul = new THREE.Mesh(new THREE.BoxGeometry(0.06, 1.28, 0.08), frameW); mul.position.set(i * w / 3.2, 1.75 + f * 2.8, s * (d / 2 + 0.035)); grp.add(mul);
    });
  }
  [1, -1].forEach(s => { const ws = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.3, 0.05), M.glass); ws.position.set(s * (w / 2 + 0.02), 1.75, 0); ws.rotation.y = Math.PI / 2; grp.add(ws); });
  // дверь, крыльцо, печная труба, иногда «тарелка»
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.95, 2.05, 0.06), new THREE.MeshStandardMaterial({ color: 0x5a3a24, roughness: 0.6 })); door.position.set(0, 0.4 + 1.03, d / 2 + 0.03); grp.add(door);
  const porch = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.4, 1.3), base.material); porch.position.set(0, 0.2, d / 2 + 0.65); grp.add(porch);
  const visor = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.06, 1.1), rm); visor.position.set(0, 2.75, d / 2 + 0.5); visor.rotation.x = 0.18; grp.add(visor);
  const chim = new THREE.Mesh(new THREE.BoxGeometry(0.5, 1.6, 0.5), new THREE.MeshStandardMaterial({ color: 0x8b4a32, roughness: 0.9 })); chim.position.set(w * 0.22, wallH + 0.4 + roofH * 0.62, 0); grp.add(chim);
  if (rnd() < 0.5) { const dish = new THREE.Mesh(new THREE.CircleGeometry(0.3, 18), new THREE.MeshStandardMaterial({ color: 0xf2f2f0, side: THREE.DoubleSide })); dish.position.set(w / 2 - 0.6, wallH - 0.2, d / 2 + 0.2); dish.rotation.x = -0.4; grp.add(dish); }
  grp.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  grp.position.copy(V(px, py, 0)); grp.rotation.y = rot; scene.add(grp);
}
neighborHouse(17, 27, 9, 8, 5.6, 3.2, 0xe9dcc0, 0x7b2e22, 0, 2);       // север
neighborHouse(12, -13, 8, 8, 3.0, 3.4, 0xc9d5d9, 0x3d4f3b, 0, 1);    // юг
neighborHouse(45, 4, 10, 8, 3.0, 3.5, 0xd8cdbb, 0x5a3b2c, Math.PI / 2, 1); // через улицу
neighborHouse(46, 25, 8, 8, 5.4, 3.0, 0xf0ead8, 0x2f3c4c, Math.PI / 2, 2);
neighborHouse(-20, 32, 9, 7, 3.2, 3.4, 0xe2d0b4, 0x6d2a1f, 0.3, 1);
{
  const walls = [0xe8dcc4, 0xd3dde0, 0xf1e7cf, 0xc9b9a0, 0xdfe6d8, 0xe9e2d6], roofs = [0x7b2e22, 0x2f3c4c, 0x3d4f3b, 0x5a3b2c, 0x6b6e70];
  // дальше по нашей стороне улицы и напротив — дома каждые ~24 м
  [-58, -40, 52, 76].forEach((sOff, i) => { const p = along(B, sOff, -12); neighborHouse(p[0], p[1], rr(8, 10), rr(7, 9), rnd() < 0.5 ? 3.0 : 5.5, rr(2.8, 3.6), walls[i % 6], roofs[i % 5], 0, rnd() < 0.5 ? 1 : 2); });
  [-50, -26, 48, 72, 96].forEach((sOff, i) => { const p = along(B, sOff, 21); neighborHouse(p[0], p[1], rr(8, 10), rr(7, 9), rnd() < 0.5 ? 3.0 : 5.5, rr(2.8, 3.6), walls[(i + 3) % 6], roofs[(i + 2) % 5], Math.PI / 2, rnd() < 0.5 ? 1 : 2); });
  [[-30, -32], [54, -40], [-40, 60], [8, 63], [70, -40], [-55, 0]].forEach(([x, y], i) => neighborHouse(x, y, rr(8, 11), rr(7, 9), 3.1, rr(3, 3.8), walls[(i + 1) % 6], roofs[i % 5], rr(-0.2, 0.2), 1));
  [[-30, 45], [62, 50], [-45, -38], [75, 10], [35, -45], [8, 52]].forEach(([x, y]) => tree(x, y, { h: rr(9, 13), r: rr(2.6, 3.6), birch: rnd() < 0.3, color: rnd() < 0.5 ? 0x47702a : 0x5a8530 }));
}
// хозпостройки соседей: теплицы из поликарбоната и сараи
function greenhouse(px, py, rot = 0) {
  const g = new THREE.Group(), pm = new THREE.MeshStandardMaterial({ color: 0xf2f5f2, transparent: true, opacity: 0.45, roughness: 0.25, side: THREE.DoubleSide, depthWrite: false });
  const arch = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 6, 18, 1, true, 0, Math.PI), pm); arch.rotation.z = Math.PI / 2; arch.rotation.y = Math.PI / 2; g.add(arch);
  [-3, 3].forEach(z => { const cap = new THREE.Mesh(new THREE.CircleGeometry(1.5, 18, 0, Math.PI), pm); cap.position.z = z; g.add(cap); });
  for (let z = -3; z <= 3; z += 1) { const rib = new THREE.Mesh(new THREE.TorusGeometry(1.5, 0.02, 4, 18, Math.PI), M.steel); rib.position.z = z; g.add(rib); }
  g.position.copy(V(px, py, 0)); g.rotation.y = rot; scene.add(g);
}
function shed(px, py, rot = 0) {
  const g = new THREE.Group(), wm = new THREE.MeshStandardMaterial({ map: rep(T.slats, 3, 2.4), color: 0x9a7a58, roughness: 0.8 });
  const body = new THREE.Mesh(new THREE.BoxGeometry(3, 2.3, 4), wm); body.position.y = 1.15; g.add(body);
  const roof = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.06, 4.4), new THREE.MeshStandardMaterial({ color: 0x4d4f52, roughness: 0.6, metalness: 0.4 })); roof.position.y = 2.42; roof.rotation.z = 0.12; g.add(roof);
  g.traverse(o => { if (o.isMesh) { o.castShadow = o.receiveShadow = true; } });
  g.position.copy(V(px, py, 0)); g.rotation.y = rot; scene.add(g);
}
greenhouse(4, -21, 0.05); shed(20, -24, 0); greenhouse(10, 34, 0); shed(28, 31, 0); greenhouse(53, 33, Math.PI / 2); shed(-28, 38, 0.3);
// дальний лес: кольцо-задник с нарисованным силуэтом крон (вместо гладких сфер)
{
  const W = 2048, H = 144;                         // 377 м на тайл по окружности → ~0.18 м/пкс по обеим осям
  const ft = canvasTex(W, (g, w, h) => {
    g.clearRect(0, 0, w, h);
    for (let i = 0; i < 1400; i++) {
      const x = rnd() * w, r = rr(5, 18), top = h * rr(0.12, 0.6) + r;
      g.fillStyle = hsl(rr(80, 120), rr(18, 34), rr(14, 26));
      g.beginPath(); g.ellipse(x, top, r * rr(0.8, 1.1), r * rr(1.0, 1.5), 0, 0, 6.28); g.fill();
      g.fillRect(x - r * 0.7, top, r * 1.4, h - top);
    }
  }, { w: W, h: H });
  ft.repeat.set(4, 1); ft.wrapT = THREE.ClampToEdgeWrapping;
  const band = new THREE.Mesh(new THREE.CylinderGeometry(240, 240, 26, 128, 1, true),
    new THREE.MeshStandardMaterial({ map: ft, alphaTest: 0.5, side: THREE.BackSide, roughness: 1 }));
  band.position.y = 12.5; scene.add(band);
}
// забор из профлиста на той стороне улицы
{
  const profM = new THREE.MeshStandardMaterial({ map: rep(T.metalRoof, 1, 1), color: 0x6b4a33, roughness: 0.5, metalness: 0.4, side: THREE.DoubleSide });
  const PROF = [0x4a3328, 0x1f4a32, 0x6e2a22, 0x8d9196, 0x5a3b2c, 0x2f3c4c].map(c => new THREE.MeshStandardMaterial({ map: rep(T.metalRoof, 1, 1), color: c, roughness: 0.5, metalness: 0.4, side: THREE.DoubleSide }));
  const gates = [-50, -26, 14, 36, 48, 72];
  let s0 = -62;
  gates.concat([96]).forEach((gs, i) => {
    const g0 = Math.min(gs - 2.3, 96), g1 = gs + 2.3;
    fenceRun(along(B, s0, 9.6), along(B, g0, 9.6), 2.0, PROF[i % 6], [1.2, 2.0], 3.0);
    if (gs < 96) { segBox(along(B, g0, 9.62), along(B, g1 - 1.1, 9.62), 0.05, 2.0, 0.05, PROF[(i + 2) % 6]);
      segBox(along(B, g1 - 1.0, 9.62), along(B, g1, 9.62), 0.05, 2.0, 0.05, PROF[(i + 2) % 6]); }
    s0 = g1;
  });
  void profM;
  fenceRun([B_[0], -0.2 + B_[1] - 30], [A_[0] - 0.1, -30], 1.53, M.meshFence, [0.4, 0.4]);
}
// опоры ЛЭП вдоль улицы и провода
{
  const poles = [];
  for (let s = -70; s <= 110; s += 34) { const p = along(B, s, 9.0); poles.push(p); cyl(p[0], p[1], 0, 9.5, 0.14, M.pole, 10); boxP(p[0] - 0.05, p[1] - 0.8, p[0] + 0.05, p[1] + 0.8, 8.8, 8.9, M.pole); }
  const wireM = new THREE.LineBasicMaterial({ color: 0x222222 });
  const mp = along(B, 8.4, 0.35); cyl(mp[0], mp[1], 0, 6.5, 0.04, M.steel, 8);
  boxP(mp[0] - 0.02, mp[1] - 0.2, mp[0] + 0.16, mp[1] + 0.2, 1.3, 1.95, new THREE.MeshStandardMaterial({ color: 0xb9bcbf, roughness: 0.5, metalness: 0.3 }));
  { const pl = poles.reduce((b_, p) => Math.hypot(p[0] - mp[0], p[1] - mp[1]) < Math.hypot(b_[0] - mp[0], b_[1] - mp[1]) ? p : b_), pts = [];
    for (let k = 0; k <= 16; k++) { const t = k / 16; pts.push(V(pl[0] + (mp[0] - pl[0]) * t, pl[1] + (mp[1] - pl[1]) * t, 8.7 + (6.4 - 8.7) * t - Math.sin(Math.PI * t) * 0.35)); }
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), wireM)); }
  poles.forEach((p, i) => { if (i % 2) return; const q = [p[0] - re[0] * 1.4, p[1] - re[1] * 1.4];
    segBox(p, q, 7.9, 7.98, 0.06, M.steel); boxP(q[0] - 0.25, q[1] - 0.12, q[0] + 0.25, q[1] + 0.12, 7.8, 7.92, M.fascia); });
  [-0.7, 0.7].forEach(o => {
    for (let i = 0; i < poles.length - 1; i++) {
      const a = poles[i], b = poles[i + 1], pts = [];
      for (let k = 0; k <= 16; k++) { const t = k / 16; pts.push(V(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + o, 8.95 - Math.sin(Math.PI * t) * 0.6)); }
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), wireM));
    }
  });
}

// ---------- 3D-трава: пучки-«карточки» у заборов, цоколя, дорожек и на лугу ----------
{
  T.tuft = canvasTex(128, (g, w, h) => {
    g.clearRect(0, 0, w, h);
    for (let i = 0; i < 90; i++) {
      const x = rr(0.08, 0.92) * w, l = rr(0.35, 0.97) * h, b = rr(-14, 14);
      g.strokeStyle = hsl(rr(72, 96), rr(24, 40), rr(14, 30)); g.lineWidth = rr(0.8, 1.8);
      g.beginPath(); g.moveTo(x, h); g.quadraticCurveTo(x + b * 0.2, h - l * 0.6, x + b, h - l); g.stroke();
    }
  });
  const tm = new THREE.MeshStandardMaterial({ map: T.tuft, alphaTest: 0.5, side: THREE.DoubleSide, roughness: 1 });
  tm.onBeforeCompile = sh => {             // нормаль «вверх» — пучок освещается как газон под ним, без пёстрых граней
    sh.vertexShader = sh.vertexShader.replace('#include <defaultnormal_vertex>', '#include <defaultnormal_vertex>\n\ttransformedNormal = normalMatrix * vec3( 0.0, 1.0, 0.0 );');
    sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_begin>', '#include <normal_fragment_begin>\n\tnormal = normalize( vNormal );');
  };
  const tg = new THREE.PlaneGeometry(1, 1); tg.translate(0, 0.5, 0);
  const N = 14000, inst = new THREE.InstancedMesh(tg, tm, N), d = new THREE.Object3D(); let k = 0;
  const put = (x, y, sz, ht) => { if (k >= N) return; d.position.copy(V(x, y, 0)); d.rotation.set(0, rr(0, 6.28), 0); d.scale.set(sz * rr(0.7, 1.3), ht * rr(0.6, 1.3), 1); d.updateMatrix(); inst.setMatrixAt(k++, d.matrix); };
  const line = (p, q, per, off, sz, ht) => { const L_ = Math.hypot(q[0] - p[0], q[1] - p[1]); for (let i = 0; i < L_ * per; i++) { const t = rnd(); put(p[0] + (q[0] - p[0]) * t + rr(-off, off), p[1] + (q[1] - p[1]) * t + rr(-off, off), sz, ht); } };
  // некошеная полоса вдоль заборов участка и снаружи
  [[A_, B_], [C_, D_], [D_, A_]].forEach(([p, q]) => line(p, q, 30, 0.22, 0.32, 0.3));
  // у цоколя дома
  const ho = S.house.outline.map(([a, b]) => L(a, b));
  for (let i = 0; i < ho.length; i++) line(ho[i], ho[(i + 1) % ho.length], 10, 0.12, 0.3, 0.18);
  // обочина улицы (обе стороны) и луг вокруг
  // обочина: между нашим забором и гравием, кроме калитки и въезда; и дальняя обочина
  for (const [s0, s1] of [[-120, gateY0 - B[1]], [gateY1 - B[1], pk[0][1] - B[1] - 0.3], [pk[2][1] - B[1] + 2.6, 140]]) line(along(B, s0, 0.9), along(B, s1, 0.9), 14, 0.45, 0.4, 0.4);
  line(along(B, -120, 9.2), along(B, 140, 9.2), 10, 0.4, 0.4, 0.4);
  inst.count = k;
  inst.receiveShadow = true; scene.add(inst);
}
// участки соседей: заборы из профлиста (посёлок, а не поле)
{
  const profC = [0x6b4a33, 0x3e5a46, 0x7d8285, 0x5a3b2c];
  const lot = (x0, y0, x1, y1, ci, skip = '') => {
    const pm = new THREE.MeshStandardMaterial({ map: rep(T.metalRoof, 1, 1), color: profC[ci % 4], roughness: 0.5, metalness: 0.4, side: THREE.DoubleSide });
    if (!skip.includes('s')) fenceRun([x1, y0], [x0, y0], 1.8, pm, [1.2, 1.8], 3); if (!skip.includes('n')) fenceRun([x0, y1], [x1, y1], 1.8, pm, [1.2, 1.8], 3);
    if (!skip.includes('w')) fenceRun([x0, y0], [x0, y1], 1.8, pm, [1.2, 1.8], 3); if (!skip.includes('e')) fenceRun([x1, y1], [x1, y0], 1.8, pm, [1.2, 1.8], 3);
  };
  lot(7.3, 16.6, 31.8, 40, 0, 's');      // север (общий забор — наша сетка)
  lot(-2, -30, 30.6, -0.15, 1, 'ne');    // юг (уличную сторону не ставим — закрывает вид с улицы)
  lot(-34, 22, -13, 44, 2);               // за ручьём
}
// ---------- небо, солнце (Одинцово 55.68° с.ш., 37.32° в.д., UTC+3) ----------
const sky = new Sky(); sky.scale.setScalar(4500); scene.add(sky);
const su = sky.material.uniforms;
su.turbidity.value = 1.6; su.rayleigh.value = 0.8; su.mieCoefficient.value = 0.0015; su.mieDirectionalG.value = 0.8;
const sun = new THREE.DirectionalLight(0xfff2e0, 3.2);
sun.castShadow = true;
sun.shadow.mapSize.set(HQ ? 4096 : 2048, HQ ? 4096 : 2048);
Object.assign(sun.shadow.camera, { left: -42, right: 42, top: 42, bottom: -42, near: 1, far: 300 });
sun.shadow.bias = -0.0003; sun.shadow.normalBias = 0.04; sun.shadow.radius = 4;
scene.add(sun); scene.add(sun.target);
const hemi = new THREE.HemisphereLight(0xcfe0ff, 0x3d4a2a, 0.35); scene.add(hemi);
const pmrem = new THREE.PMREMGenerator(renderer);
const skyScene = new THREE.Scene(); const skyForEnv = new Sky(); skyForEnv.scale.setScalar(4500); skyScene.add(skyForEnv);
{ const eu = skyForEnv.material.uniforms; for (const k of ['turbidity','rayleigh','mieCoefficient','mieDirectionalG']) eu[k].value = su[k].value; }
{ // земля и линия леса в env: Sky.js ниже горизонта светит как горизонт → подсветка снизу «белым небом»
  const gnd = new THREE.Mesh(new THREE.CircleGeometry(95, 48), new THREE.MeshBasicMaterial({ color: 0x5f6656 }));
  gnd.rotation.x = -Math.PI / 2; gnd.position.y = -1.6; skyScene.add(gnd);
  const tl = new THREE.Mesh(new THREE.CylinderGeometry(90, 90, 9, 48, 1, true), new THREE.MeshBasicMaterial({ color: 0x3a4a2c, side: THREE.BackSide }));
  tl.position.y = 2.6; skyScene.add(tl);
}

// облака: плоский слой на 700 м с процедурной текстурой кучевых облаков (туман гасит их у горизонта)
{
  const ct = canvasTex(1024, (g, w, h) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, w, h); g.globalCompositeOperation = 'lighter';
    for (let c = 0; c < 22; c++) {
      const cx0 = rnd() * w, cy0 = rnd() * h, R = rr(30, 90), n = Math.round(rr(14, 30));
      for (let i = 0; i < n; i++) {
        const a = rnd() * 6.28, d = Math.pow(rnd(), 0.7) * R, x = cx0 + Math.cos(a) * d * 1.6, y = cy0 + Math.sin(a) * d * 0.8, r = rr(0.35, 0.7) * R * (1 - d / R * 0.5);
        for (const ox of [-w, 0, w]) for (const oy of [-h, 0, h]) {
          const gr = g.createRadialGradient(x + ox, y + oy, 0, x + ox, y + oy, r);
          gr.addColorStop(0, 'rgba(255,255,255,0.32)'); gr.addColorStop(0.6, 'rgba(255,255,255,0.12)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
          g.fillStyle = gr; g.fillRect(x + ox - r, y + oy - r, 2 * r, 2 * r);
        }
      }
    }
  }, { srgb: false });
  ct.repeat.set(3, 3);
  const cg = new THREE.CircleGeometry(4000, 64); const cp = cg.attributes.position, ca = new Float32Array(cp.count * 4);
  for (let i = 0; i < cp.count; i++) { const r = Math.hypot(cp.getX(i), cp.getY(i)) / 4000; ca.set([1, 1, 1, r < 0.01 ? 1 : 0], i * 4); }
  cg.setAttribute('color', new THREE.BufferAttribute(ca, 4));
  const k = 1.8;
  const cm = new THREE.MeshBasicMaterial({ alphaMap: ct, vertexColors: true, transparent: true, depthWrite: false, fog: false, color: new THREE.Color().setRGB(k, k, k * 1.02, THREE.LinearSRGBColorSpace) });
  ct.repeat.set(5, 5);
  const cl = new THREE.Mesh(cg, cm); cl.rotation.x = Math.PI / 2; cl.position.y = 700; cl.renderOrder = -1; scene.add(cl);
}
let envRT = null, sunAlt = 0.6;
function applyExposure() { renderer.toneMappingExposure = 0.56 * (sunAlt > 0.05 ? 1 : 0.7) * Math.pow(2, viewEV); }

function sunPosition(dayOfYear, hourLocal) {
  const lat = 55.6837 * Math.PI / 180, lon = 37.322;
  const decl = 23.44 * Math.PI / 180 * Math.sin(2 * Math.PI * (284 + dayOfYear) / 365);
  const Bq = 2 * Math.PI * (dayOfYear - 81) / 364;
  const eot = 9.87 * Math.sin(2 * Bq) - 7.53 * Math.cos(Bq) - 1.5 * Math.sin(Bq);   // мин
  const solar = hourLocal + (4 * (lon - 45) + eot) / 60;
  const H = (solar - 12) * 15 * Math.PI / 180;
  const alt = Math.asin(Math.sin(lat) * Math.sin(decl) + Math.cos(lat) * Math.cos(decl) * Math.cos(H));
  let az = Math.atan2(Math.sin(H), Math.cos(H) * Math.sin(lat) - Math.tan(decl) * Math.cos(lat)) + Math.PI; // от севера по часовой
  return { alt, az };
}
const NORTH = THREE.MathUtils.degToRad(S.north_deg);  // север повёрнут от «верха» плана против часовой
function setSun(dayOfYear, hour) {
  const { alt, az } = sunPosition(dayOfYear, hour);
  // вектор на север в плане: поворот (0,1) на |north_deg| против часовой → (−sin θ, cos θ), θ = −north_deg
  const th = -NORTH; const nP = [-Math.sin(th), Math.cos(th)], eP = [Math.cos(th), Math.sin(th)];
  const hx = nP[0] * Math.cos(az) + eP[0] * Math.sin(az), hy = nP[1] * Math.cos(az) + eP[1] * Math.sin(az);
  const dir = new THREE.Vector3(hx * Math.cos(alt), Math.sin(alt), -hy * Math.cos(alt)).normalize();
  su.sunPosition.value.copy(dir); skyForEnv.material.uniforms.sunPosition.value.copy(dir);
  const up = Math.max(0, Math.sin(alt));
  sun.position.copy(dir.clone().multiplyScalar(120)); sun.target.position.set(0, 0, 0);
  sun.intensity = 4.6 * Math.min(1, up * 2.2);
  sun.color.setHSL(0.09, 0.6, 0.6 + 0.3 * Math.min(1, up * 2));
  hemi.intensity = 0.1 + 0.15 * Math.min(1, up * 2);
  sunAlt = alt; applyExposure();
  if (envRT) envRT.dispose();
  envRT = pmrem.fromScene(skyScene, 0.02);
  scene.environment = envRT.texture;
  // дымка теплеет к закату
  const kf = THREE.MathUtils.clamp(alt / 0.35, 0, 1);
  scene.fog.color.setRGB(0.8 + 0.25 * (1 - kf), 0.95 - 0.1 * (1 - kf), 1.2 - 0.45 * (1 - kf), THREE.LinearSRGBColorSpace);
  if (alt < 0) scene.fog.color.multiplyScalar(0.4);
  renderer.shadowMap.needsUpdate = true; dirty = true;
  return { alt: THREE.MathUtils.radToDeg(alt), az: THREE.MathUtils.radToDeg(az) };
}

// ---------- камеры ----------
let viewEV = 0;
const VIEWS = {
  aerial:   { pos: [41, -17, 24], target: [17, 9, 0], fov: 40, ev: 0.35 },
  backyard: { pos: [-9, -13, 15], target: [12, 8, 0], fov: 40, ev: 0.35 },
  entry:    { pos: [35.2, 13.6, 2.6], target: [21, 6.6, 1.1], fov: 52, ev: 0.6 },   // с улицы в открытые ворота, контровой свет
  garden:   { pos: [4.3, 4.6, 1.7], target: [13, 7.0, 1.0], fov: 60, ev: 0.5 },
  top:      { pos: [cx, cy - 0.01, 70], target: [cx, cy, 0], fov: 32, ev: 0.25 },
  street:   { pos: [37.0, -6, 1.7], target: [24, 8, 1.8], fov: 52, ev: 0.2 },
};
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.maxPolarAngle = Math.PI / 2 - 0.03; controls.minDistance = 3; controls.maxDistance = 160;
let currentView = 'aerial';
function fitFov(vfov) {                              // на вертикальном экране сохраняем горизонтальный охват кадра 16:10
  const a = camera.aspect || 1.6;
  if (a >= 1.6) return vfov;
  const t = Math.tan(THREE.MathUtils.degToRad(vfov) / 2) * 1.6 / a;
  return Math.min(88, THREE.MathUtils.radToDeg(2 * Math.atan(t)));
}
function setView(name) {
  const dmp = controls.enableDamping; controls.enableDamping = false; controls.update(); controls.enableDamping = dmp;
  const v = VIEWS[name] || VIEWS.aerial; viewEV = v.ev || 0; applyExposure(); currentView = name;
  camera.fov = fitFov(v.fov); camera.position.copy(V(v.pos[0], v.pos[1], v.pos[2]));
  controls.target.copy(V(v.target[0], v.target[1], v.target[2]));
  camera.up.set(0, 1, 0);
  camera.lookAt(controls.target); camera.updateProjectionMatrix(); controls.update();
  if (typeof gateOpen === 'function') gateOpen(name === 'entry');
  dirty = true;
}

// ---------- запуск ----------
let composer = null;
function resize() {
  const w = canvas.clientWidth || window.innerWidth, h = canvas.clientHeight || window.innerHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h; dirty = true;
  if (typeof currentView !== 'undefined' && VIEWS[currentView]) camera.fov = fitFov(VIEWS[currentView].fov);
  camera.updateProjectionMatrix();
  if (composer) composer.setSize(w, h);
}
window.addEventListener('resize', resize);
resize();

const DAY = { june: 172, sept: 264, may: 135 };
const state = { day: DAY[params.get('day')] || DAY.june, hour: parseFloat(params.get('hour') || '16'), view: params.get('view') || 'aerial' };
setView(state.view);
setSun(state.day, state.hour);

if (HQ) {
  const [{ EffectComposer }, { RenderPass }, { GTAOPass }, { SMAAPass }, { OutputPass }] = await Promise.all(
    ['EffectComposer', 'RenderPass', 'GTAOPass', 'SMAAPass', 'OutputPass'].map(n => import(`three/addons/postprocessing/${n}.js`)));
  renderer.shadowMap.needsUpdate = true;
  composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const w = canvas.clientWidth, h = canvas.clientHeight;
  const ao = new GTAOPass(scene, camera, w, h); ao.output = GTAOPass.OUTPUT.Default; ao.setSceneClipBox(new THREE.Box3(new THREE.Vector3(-90, -3, -90), new THREE.Vector3(90, 40, 90)));
  ao.updateGtaoMaterial({ radius: 0.6, distanceExponent: 1, thickness: 1, scale: 1.2 });
  ao.blendIntensity = 0.85;
  // GTAO рисует G-буфер без альфа-теста: листва и сетка забора дали бы квадратные пятна — прячем их на этот проход
  const ov = ao.overrideVisibility.bind(ao);
  ao.overrideVisibility = function () { ov(); this.scene.traverse(o => { if (o.material && o.material.alphaTest > 0) o.visible = false; }); };
  composer.addPass(ao);
  composer.addPass(new OutputPass());
  const smaa = new SMAAPass(w, h);
  await Promise.all([smaa.areaTexture.image.decode(), smaa.searchTexture.image.decode()]).catch(() => {});
  smaa.areaTexture.needsUpdate = smaa.searchTexture.needsUpdate = true;
  composer.addPass(smaa);
  composer.setSize(w, h);
  composer.render();
  requestAnimationFrame(() => { composer.render(); window.__ready = true; });
} else {
  const lp = new THREE.Vector3(), lq = new THREE.Quaternion();
  renderer.setAnimationLoop(() => {               // рисуем только при видимом движении камеры — бережём батарею телефона
    controls.update();
    if (dirty || lp.distanceToSquared(camera.position) > 1e-6 || 8 * (1 - Math.abs(lq.dot(camera.quaternion))) > 1e-6) {
      lp.copy(camera.position); lq.copy(camera.quaternion); renderer.render(scene, camera); dirty = false;
    }
  });
  window.__ready = true;
}

// API для интерфейса страницы
window.plot3d = {
  setView, VIEWS,
  setSun: (day, hour) => { state.day = day; state.hour = hour; return setSun(day, hour); },
  DAY,
};
document.dispatchEvent(new CustomEvent('plot3d-ready'));
