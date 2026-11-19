const puppeteer=require(process.env.PUPPETEER_PATH||'puppeteer');
const assert=require('node:assert/strict');
const path=require('node:path');
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage();
  await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.UTRO7_URL||'file://'+path.resolve(__dirname,'../index.html'),{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>localStorage.clear());await page.reload({waitUntil:'domcontentloaded'});
  assert.match(await page.$eval('.feature-caption',e=>e.textContent),/Отжимания · 30 секунд/);
  assert.equal(await page.$('#open-catalog'),null);
  assert.equal(await page.$('#open-builder'),null);
  await page.click('#preview-moves');
  assert.equal(await page.$eval('.work-progress',e=>e.textContent.trim()),'1 из 1');
  assert.equal(await page.$eval('.work-title',e=>e.textContent.trim()),'Отжимания');
  assert.ok(await page.$('iframe.trainer-3d-frame'));
  assert.equal(await page.$('svg.moving-figure'),null);
  await page.click('#guide-start');
  assert.equal(await page.$eval('#exercise-name',e=>e.textContent.trim()),'Отжимания');
  assert.ok(await page.$('iframe.trainer-3d-frame'));
  assert.equal(await page.$('#workout-avatar'),null);
  await page.click('#pushup-mode');
  assert.ok(await page.$('video.pushup-real-video'));
  await page.click('#pushup-mode');
  assert.ok(await page.$('iframe.trainer-3d-frame'));
  await page.evaluate(()=>{const orig=Date.now.bind(Date);Date.now=()=>orig()+9000;});
  await new Promise(r=>setTimeout(r,350));
  assert.equal(await page.$eval('#progress-label',e=>e.textContent.trim()),'1 из 1 упражнений');
  assert.equal(errors.length,0,errors.join('; '));
  console.log('PASS_PILOT_ONE_PUSHUP',JSON.stringify({exercise:'Отжимания',count:1,avatar:'3d sportswear CC0 prototype',errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error('PILOT_SMOKE_FAIL',e.stack);process.exitCode=1});
