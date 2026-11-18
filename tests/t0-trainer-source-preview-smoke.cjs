const puppeteer=require(process.env.PUPPETEER_PATH||'puppeteer');
const path=require('path');
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage();
 await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1});
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const url=process.env.T0_PREVIEW_URL || 'file://'+path.resolve(__dirname,'../preview/trainer-master-t0/index.html');
 await page.goto(url,{waitUntil:'domcontentloaded',timeout:30000});
 const check=await page.evaluate(async()=>{
   const imgs=[...document.querySelectorAll('figure img')];
   const checks=await Promise.all(imgs.map(e=>new Promise(resolve=>{
     const probe=new Image();
     probe.onload=()=>resolve({src:e.getAttribute('src'),width:probe.naturalWidth,height:probe.naturalHeight,loaded:true});
     probe.onerror=()=>resolve({src:e.getAttribute('src'),loaded:false});
     probe.src=e.src;
   })));
   return {images:checks,bodyWidth:document.body.scrollWidth,viewportWidth:document.documentElement.clientWidth,
     notApproved:/НЕ ПРИНЯТО|Технически отклонено|не соответствует техническим требованиям/i.test(document.body.textContent),
     hasT0:document.body.textContent.includes('T0')};
 });
 console.log(JSON.stringify({imageCount:check.images.length,allLoaded:check.images.every(i=>i.loaded),
  minWidth:Math.min(...check.images.map(i=>i.width||0)),notApproved:check.notApproved,
  hasT0:check.hasT0,overflow:check.bodyWidth-check.viewportWidth,errors},null,2));
 await browser.close();
 if(check.images.length!==7||check.images.some(i=>!i.loaded)||!check.notApproved||!check.hasT0||
   check.bodyWidth>check.viewportWidth+2||errors.length)process.exitCode=1;
})().catch(e=>{console.error('T0_PREVIEW_ERROR',e.stack);process.exitCode=2});
