const puppeteer=require(process.env.PUPPETEER_PATH||'puppeteer');
const path=require('path');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
 const page=await browser.newPage();
 await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const url=process.env.SQUAT_PREVIEW_URL||'file://'+path.resolve(__dirname,'../preview/squat-g1/index.html');
 await page.goto(url,{waitUntil:'domcontentloaded',timeout:30000});
 await page.waitForFunction(()=>{const v=document.querySelector('#motion');return v&&v.readyState>=2},{timeout:12000});
 const initial=await page.$eval('#motion',v=>({
   width:v.videoWidth,height:v.videoHeight,duration:v.duration,muted:v.muted,
   inline:v.hasAttribute('playsinline'),loop:v.loop,src:v.currentSrc,t:v.currentTime
 }));
 await sleep(420);
 const move=await page.$eval('#motion',v=>v.currentTime);
 await page.click('#play');
 const paused0=await page.$eval('#motion',v=>v.currentTime);
 await sleep(340);
 const paused1=await page.$eval('#motion',v=>v.currentTime);
 await page.click('#speed');
 const rate=await page.$eval('#motion',v=>v.playbackRate);
 await page.click('#restart');
 const restarted=await page.$eval('#motion',v=>v.currentTime);
 await page.$eval('#scrub',el=>{el.value='1500';el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));});
 await sleep(160);
 const scrubTime=await page.$eval('#motion',v=>v.currentTime);
 await page.click('#play');
 const resume0=await page.$eval('#motion',v=>v.currentTime);
 await sleep(400);
 const resume1=await page.$eval('#motion',v=>v.currentTime);
 const viewport=await page.evaluate(()=>({scroll:document.body.scrollWidth,client:document.documentElement.clientWidth}));
 const result={initial,move,paused:Math.abs(paused1-paused0)<.07,rate,restarted,scrubTime,resumed:resume1>resume0+.1,viewport,errors};
 console.log(JSON.stringify(result,null,2));
 await browser.close();
 if(errors.length||!initial.src.endsWith('female-squat-candidate.mp4')||
    initial.width!==800||initial.height!==800||Math.abs(initial.duration-4.0)>.05||
    !initial.muted||!initial.inline||!initial.loop||move<initial.t+.1||
    !result.paused||Math.abs(rate-.5)>.01||restarted>.05||
    Math.abs(scrubTime-1.5)>.15||!result.resumed||viewport.scroll>viewport.client+2)
   process.exitCode=1;
})().catch(e=>{console.error('SQUAT_SMOKE_ERROR',e.stack);process.exitCode=2});
