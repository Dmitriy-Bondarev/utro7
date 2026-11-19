const puppeteer = require(process.env.PUPPETEER_PATH || 'puppeteer');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const path = require('node:path');
(async () => {
  const browser = await puppeteer.launch({headless: true, args: ['--no-sandbox']});
  try {
    for (const preference of ['no-preference', 'reduce']) {
      const page = await browser.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.setViewport({width: 390, height: 844});
      await page.emulateMediaFeatures([{name:'prefers-reduced-motion', value:preference}]);
      await page.goto(process.env.UTRO7_URL || 'file://' + path.resolve(__dirname, '../index.html'), {waitUntil:'domcontentloaded'});
      await page.click('#start');
      const video = await page.waitForSelector('video.pushup-real-video');
      await page.waitForFunction(() => document.querySelector('video.pushup-real-video')?.readyState >= 2);
      const t0 = await page.$eval('video.pushup-real-video', v => v.currentTime);
      const frame0 = crypto.createHash('sha256').update(await video.screenshot()).digest('hex');
      await new Promise(r => setTimeout(r, 1200));
      const t1 = await page.$eval('video.pushup-real-video', v => v.currentTime);
      const frame1 = crypto.createHash('sha256').update(await video.screenshot()).digest('hex');
      assert.ok(t1-t0 > 0.65, 'Video did not advance under ' + preference);
      assert.notEqual(frame0, frame1, 'Rendered frames are identical under ' + preference);
      await page.click('#stop-play');
      const onPause = await page.$eval('video.pushup-real-video', v => ({paused:v.paused,time:v.currentTime}));
      assert.equal(onPause.paused,true, 'Workout pause must stop trainer');
      await page.click('#stop-play');
      await page.waitForFunction(() => !document.querySelector('video.pushup-real-video')?.paused);
      const t2 = await page.$eval('video.pushup-real-video', v => v.currentTime);
      await new Promise(r => setTimeout(r, 700));
      const t3 = await page.$eval('video.pushup-real-video', v => v.currentTime);
      assert.ok(t3-t2 > 0.4, 'Playback did not resume');
      assert.deepEqual(errors, []);
      console.log('PASS_PUSHUP_PLAYBACK', JSON.stringify({preference,videoStarted:true,frameChange:true,workoutPause:true,resume:true,timeAdvanced:t1-t0}));
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(e=>{console.error('PUSHUP_PLAYBACK_FAIL',e.stack);process.exitCode=1});
