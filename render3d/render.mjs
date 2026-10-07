// Рендер кадров 3D-сцены в PNG через headless Chromium (WebGL на SwiftShader).
// node render.mjs <url-базы> <папка-вывода> view:hour[:day] ...
import { chromium } from 'playwright-core';

const [base, outDir, ...shots] = process.argv.slice(2);
const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
for (const shot of shots) {
  const [view, hour = '16', day = 'june', w = '1600', h = '1000'] = shot.split(':');
  const page = await browser.newPage({ viewport: { width: +w, height: +h } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  const t0 = Date.now();
  await page.goto(`${base}?hq=1&view=${view}&hour=${hour}&day=${day}`);
  try {
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 240000 });
  } catch (e) {
    console.log('TIMEOUT', view, errors.join('\n')); await page.close(); continue;
  }
  await page.waitForTimeout(500);
  const file = `${outDir}/${view}-${hour}-${day}.png`;
  await page.screenshot({ path: file });
  console.log(file, `${((Date.now() - t0) / 1000).toFixed(1)}s`, errors.length ? 'ERR: ' + errors.join(' | ') : '');
  await page.close();
}
await browser.close();
