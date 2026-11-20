const puppeteer=require(process.env.PUPPETEER_PATH||'puppeteer');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox']});
 try{
 const page=await browser.newPage();
 await page.setViewport({width:960,height:860});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.UTRO7_URL||'http://127.0.0.1:8768/',{waitUntil:'domcontentloaded'});
 await page.evaluate(()=>document.querySelector('#start').click());
 await page.waitForFunction(()=>document.querySelector('iframe.trainer-3d-frame')?.contentWindow?.__utro7Real3D?.loaded,{timeout:20000});
 const fr=page.frames().find(f=>f.url().includes('/preview/rotatable-cc0-trainer/'));
 assert.ok(fr,'3D viewer frame absent');
 const pos=()=>fr.evaluate(()=>window.__utro7Real3D.camera.position.toArray());
 const orig=await pos();
 await fr.click('#side');
 await new Promise(r=>setTimeout(r,240));
 const changed=await pos();
 assert.ok(orig.reduce((acc,x,i)=>acc+Math.abs(x-changed[i]),0)>.45,'Side view did not change angle');
 await fr.click('#reset');
 await new Promise(r=>setTimeout(r,300));
 const reset=await pos();
 assert.ok(orig.reduce((acc,x,i)=>acc+Math.abs(x-reset[i]),0)<.03,'3/4 did not reset to original camera');
 const canvas=await fr.$('#stage canvas');
 const rect=await canvas.boundingBox();
 await page.mouse.move(rect.x+rect.width*.5,rect.y+rect.height*.5);
 await page.mouse.wheel({deltaY:-8500});
 await new Promise(r=>setTimeout(r,460));
 const zoomed=await pos();
 const distance=Math.hypot(zoomed[0],zoomed[1]-.4,zoomed[2]);
 assert.ok(distance>1.75, 'Unsafe camera zoom allowed: '+distance);
 await fr.click('#reset');await new Promise(r=>setTimeout(r,290));
 const final=await pos();
 assert.ok(orig.reduce((acc,x,i)=>acc+Math.abs(x-final[i]),0)<.03,'Reset after zoom failed');
 assert.deepEqual(errors,[]);
 console.log('PASS_MALE_CAMERA_FRAME',JSON.stringify({sideAngle:true,reset:true,minimumDistance:distance,resetAfterZoom:true,errors}));
 }finally{await browser.close()}
})().catch(e=>{console.error('FAIL_MALE_CAMERA_FRAME',e.stack);process.exitCode=1});