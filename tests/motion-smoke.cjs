const puppeteer=require(process.env.PUPPETEER_PATH||'puppeteer');
const assert=require('node:assert/strict');
const path=require('node:path');
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage(); const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.UTRO7_URL||'file://'+path.resolve(__dirname,'../index.html'),{waitUntil:'domcontentloaded'});
  const registry=await page.evaluate(()=>({total:window.Utro7MotionPolicy?.all().length,rejected:window.Utro7MotionPolicy?.getStatus('pushup','trainer_female_01')}));
  assert.equal(registry.total,9);assert.equal(registry.rejected,'rejected');
  await page.evaluate(()=>document.getElementById('start').click());
  const display=await page.evaluate(()=>({title:document.querySelector('#exercise-name')?.textContent,
   has3d:!!document.querySelector('iframe.trainer-3d-frame'),
   hasSchematic:!!document.querySelector('svg.moving-figure'),
   label:document.querySelector('.motion-badge')?.textContent}));
  assert.equal(display.title,'Отжимания');assert.ok(display.has3d);
  assert.equal(display.hasSchematic,false);assert.match(display.label,/3D · спортивный прототип/);
  await page.click('#pushup-mode');
  assert.ok(await page.$('video.pushup-real-video'));
  assert.equal(errors.length,0,errors.join('; '));
  console.log('PASS_MOTION_PILOT',JSON.stringify({registry,display,errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error('MOTION_PILOT_FAIL',e.stack);process.exitCode=1});
