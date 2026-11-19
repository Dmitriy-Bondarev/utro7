const puppeteer = require(process.env.PUPPETEER_PATH || 'puppeteer');
const assert = require('node:assert/strict');

(async () => {
  const base = process.env.UTRO7_URL || 'http://127.0.0.1:8768/';
  const preview = new URL('preview/digital-human-studio/', base).href;
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-webgl']
  });
  const report = { desktop: {}, mobile: {}, app: {}, errors: [] };
  try {
    const page = await browser.newPage();
    page.on('pageerror', error => report.errors.push('desktop ' + error.message));
    page.on('response', res => {
      if (res.status() >= 400) report.errors.push('desktop HTTP ' + res.status() + ' ' + res.url());
    });
    await page.setViewport({ width: 1240, height: 850, deviceScaleFactor: 1 });
    await page.goto(preview, { waitUntil: 'networkidle0', timeout: 30000 });
    await page.waitForFunction(() => window.__utro7Viewer?.cameraControlsReady, { timeout: 12000 });
    report.desktop = await page.evaluate(() => ({
      hasCanvas: document.querySelectorAll('#stage canvas').length === 1,
      modelMode: window.__utro7Viewer.modelMode,
      widthOverflow: document.body.scrollWidth - innerWidth,
      readyMessage: document.querySelector('#status')?.textContent
    }));
    await page.click('#playPause');
    assert.equal(await page.evaluate(() => window.__utro7Viewer.playing), true);
    await page.click('[data-camera="side"]');
    await page.$eval('#pose', el => {
      el.value = '100';
      el.dispatchEvent(new Event('input', { bubbles: true }));
    });
    report.desktop.afterPose = await page.evaluate(() => ({
      playing: window.__utro7Viewer.playing,
      selectedSide: document.querySelector('[data-camera="side"]').getAttribute('aria-pressed'),
      slider: document.querySelector('#pose').value
    }));
    assert.equal(report.desktop.hasCanvas, true);
    assert.equal(report.desktop.modelMode, 'procedural-skeleton-demo');
    assert.ok(report.desktop.widthOverflow <= 2);
    assert.equal(report.desktop.afterPose.playing, false);
    assert.equal(report.desktop.afterPose.selectedSide, 'true');
    assert.equal(report.desktop.afterPose.slider, '100');

    const mobile = await browser.newPage();
    mobile.on('pageerror', error => report.errors.push('mobile ' + error.message));
    await mobile.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 1 });
    await mobile.goto(preview, { waitUntil: 'networkidle0', timeout: 30000 });
    await mobile.waitForFunction(() => window.__utro7Viewer?.cameraControlsReady);
    report.mobile = await mobile.evaluate(() => ({
      canvas: !!document.querySelector('#stage canvas'),
      overflow: document.body.scrollWidth - document.documentElement.clientWidth,
      controls: [...document.querySelectorAll('[data-camera]')].length
    }));
    assert.equal(report.mobile.canvas, true);
    assert.ok(report.mobile.overflow <= 2, 'mobile horizontal overflow');
    assert.equal(report.mobile.controls, 4);

    const app = await browser.newPage();
    app.on('pageerror', error => report.errors.push('app ' + error.message));
    await app.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true });
    await app.goto(base, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await app.evaluate(() => { localStorage.clear(); window.__labOpened = null; window.open = u => { window.__labOpened = u; return null; }; });
    await app.reload({ waitUntil: 'domcontentloaded' });
    await app.evaluate(() => { window.open = u => { window.__labOpened = u; return null; }; });
    await app.click('#open-presets');
    await app.click('[data-detail="morning7"]');
    await app.click('[data-workout-move="2"]');
    report.app.guideVideo = !!(await app.$('video.pushup-real-video'));
    report.app.guideLabHidden = !(await app.$('#guide-3d-lab'));
    assert.equal(report.app.guideVideo, true);
    assert.equal(report.app.guideLabHidden, true);
    await app.click('#guide-home');
    await app.click('#workout-detail-start');
    await app.evaluate(() => { const original = Date.now.bind(Date); Date.now = () => original() + 78000; });
    await new Promise(r => setTimeout(r, 500));
    report.app.exercise = await app.$eval('#exercise-name', el => el.textContent);
    report.app.workoutVideo = !!(await app.$('video.pushup-real-video'));
    report.app.workoutLabHidden = !(await app.$('#workout-3d-lab'));
    assert.equal(report.app.exercise, 'Отжимания');
    assert.equal(report.app.workoutVideo, true);
    assert.equal(report.app.workoutLabHidden, true);
    await app.click('#stop-play');
    report.app.workoutPaused = await app.evaluate(() => !!document.querySelector('.workout.paused'));
    assert.equal(report.app.workoutPaused, true);
    assert.equal(report.errors.length, 0, report.errors.join('\n'));
    console.log('PASS_DIGITAL_HUMAN_STUDIO', JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
})().catch(err => { console.error('DIGITAL_HUMAN_STUDIO_FAILURE', err.stack); process.exitCode = 1; });
