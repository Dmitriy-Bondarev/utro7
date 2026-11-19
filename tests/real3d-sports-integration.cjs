const puppeteer=require(process.env.PUPPETEER_PATH||'puppeteer');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
(async()=>{
const browser=await puppeteer.launch({headless:true,args:['--no-sandbox','--enable-webgl','--use-angle=swiftshader']});
try{
 const page=await browser.newPage();
 await page.setViewport({width:430,height:900,isMobile:true,hasTouch:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.UTRO7_URL||'http://127.0.0.1:8768/',{waitUntil:'domcontentloaded'});
 await page.evaluate(()=>document.querySelector('#start')?.click());
 await page.waitForFunction(()=>document.querySelector('iframe.trainer-3d-frame')?.contentWindow?.__utro7Real3D?.loaded,{timeout:20000});
 const state=()=>page.evaluate(()=>{const w=document.querySelector('iframe.trainer-3d-frame')?.contentWindow;
  return {position:w?.__utro7Real3D?.camera?.position.toArray(),playing:w?.__utro7Real3D?.playing,
  model:w?.__utro7Real3D?.modelType};});
 const first=await state();
 assert.equal(first.model,'cc0-sportswear-not-approved');assert.equal(first.playing,true);
 const frame=await (await page.$('iframe.trainer-3d-frame')).contentFrame();
 const canvas=await frame.$('#stage canvas');
 const digest=async()=>crypto.createHash('sha256').update(await canvas.screenshot()).digest('hex');
 const t0=await digest();await new Promise(r=>setTimeout(r,650));const t1=await digest();
 assert.notEqual(t0,t1,'Animation frames should change, not just stay a still image');
 const rect=await canvas.boundingBox();
 await page.mouse.move(rect.x+rect.width*.68,rect.y+rect.height*.55);
 await page.mouse.down();
 await page.mouse.move(rect.x+rect.width*.25,rect.y+rect.height*.55,{steps:14});
 await page.mouse.up();await new Promise(r=>setTimeout(r,250));
 const moved=await state();
 assert.ok(first.position.reduce((s,x,i)=>s+Math.abs(x-moved.position[i]),0)>.3,'Camera must rotate with mouse');
 await page.evaluate(()=>document.querySelector('#stop-play').click());
 await page.waitForFunction(()=>{const w=document.querySelector('iframe.trainer-3d-frame')?.contentWindow;return w?.__utro7Real3D?.loaded&&!w.__utro7Real3D.playing;},{timeout:20000});
 await page.evaluate(()=>document.querySelector('#stop-play').click());
 await page.waitForFunction(()=>document.querySelector('iframe.trainer-3d-frame')?.contentWindow?.__utro7Real3D?.playing,{timeout:20000});
 await page.evaluate(()=>document.querySelector('#pushup-mode').click());
 assert.ok(await page.$('video.pushup-real-video'));
 await page.evaluate(()=>document.querySelector('#pushup-mode').click());
 await page.waitForFunction(()=>document.querySelector('iframe.trainer-3d-frame')?.contentWindow?.__utro7Real3D?.loaded,{timeout:20000});
 assert.deepEqual(errors,[]);
 console.log('PASS_SPORTS_3D_INTEGRATION',JSON.stringify({animationFramesDiffer:true,rotation:true,pause:true,resume:true,videoFallback:true,errors}));
}finally{await browser.close();}
})().catch(e=>{console.error('SPORTS_3D_INTEGRATION_FAIL',e.stack);process.exitCode=1});