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
  await page.click('#start');
  const display=await page.evaluate(()=>({title:document.querySelector('#exercise-name')?.textContent,
   hasVideo:!!document.querySelector('video.pushup-real-video'),
   hasSchematic:!!document.querySelector('svg.moving-figure'),
   label:document.querySelector('.motion-badge')?.textContent}));
  assert.equal(display.title,'Отжимания');assert.ok(display.hasVideo);
  assert.equal(display.hasSchematic,false);assert.match(display.label,/видеопрототип/);
  assert.equal(errors.length,0,errors.join('; '));
  console.log('PASS_MOTION_PILOT',JSON.stringify({registry,display,errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error('MOTION_PILOT_FAIL',e.stack);process.exitCode=1});
