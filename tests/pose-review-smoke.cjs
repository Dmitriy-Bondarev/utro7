const puppeteer = require(process.env.PUPPETEER_PATH||'puppeteer');
const path = require('path');

(async()=>{
  const browser=await puppeteer.launch({headless:true,args:['--no-sandbox']});
  const page=await browser.newPage();
  await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.POSE_URL||'file://'+path.resolve(__dirname,'../preview/pushup-v3/index.html'),{waitUntil:'domcontentloaded'});
  const initial=await page.$eval('#poseImage',e=>({src:e.currentSrc,loaded:e.complete&&e.naturalWidth>0,width:e.naturalWidth}));
  await page.click('[data-pose="P3"]');
  await page.waitForFunction(()=>document.querySelector('#poseImage').complete && document.querySelector('#poseImage').naturalWidth>0);
  const low=await page.$eval('#poseImage',e=>({src:e.src,loaded:e.complete&&e.naturalWidth>0}));
  await page.select('#camera','B_three_quarter');
  await page.waitForFunction(()=>document.querySelector('#poseImage').complete && document.querySelector('#poseImage').naturalWidth>0);
  const quarter=await page.$eval('#poseImage',e=>({src:e.currentSrc,loaded:e.naturalWidth>0}));
  await page.select('#camera','C_front');
  await page.click('[data-pose="P5"]');
  await page.waitForFunction(()=>document.querySelector('#poseImage').complete && document.querySelector('#poseImage').naturalWidth>0);
  const front=await page.$eval('#poseImage',e=>({src:e.currentSrc,loaded:e.naturalWidth>0}));
  const sheet=await page.$eval('.sheet',e=>({loaded:e.complete&&e.naturalWidth>0,width:e.naturalWidth}));
  const viewport=await page.evaluate(()=>({body:document.body.scrollWidth,viewport:document.documentElement.clientWidth}));
  await page.screenshot({path:'/tmp/utro7-g1-pose-review-mobile.png'});
  const result={initial,low,quarter,front,sheet,viewport,errors};
  console.log(JSON.stringify(result,null,2));
  await browser.close();
  if(errors.length||!initial.loaded||!initial.src.endsWith('A_side_P0.jpg')||
    !low.loaded||!low.src.endsWith('A_side_P3.jpg')||!quarter.src.endsWith('B_three_quarter_P3.jpg')||
    !front.src.endsWith('C_front_P5.jpg')||!front.loaded||!sheet.loaded||
    viewport.body>viewport.viewport+2)process.exitCode=1;
})().catch(e=>{console.error('POSE_REVIEW_QA_ERROR',e.stack);process.exitCode=2});
