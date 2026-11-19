const puppeteer = require(process.env.PUPPETEER_PATH || 'puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({headless:true,args:['--no-sandbox']});
  const page = await browser.newPage();
  await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1});
  page.on('dialog',d=>d.accept());
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.UTRO7_URL || 'file://' + path.resolve(__dirname,'../index.html'),{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>localStorage.clear());
  await page.reload({waitUntil:'domcontentloaded'});
  const policy=await page.evaluate(()=>{
    const p=window.Utro7MotionPolicy;
    if(!p)return null;
    return {
      count:p.all().length,
      published:p.all().filter(x=>p.getApproved(x.exerciseId,x.trainerId)).length,
      pushupWoman:p.getStatus('pushup','trainer_female_01'),
      pushupMan:p.getStatus('pushup','man'),
      marchWoman:p.getStatus('march','woman')
    };
  });
  await page.click('#open-presets');
  await page.click('[data-detail="morning7"]');
  await page.click('[data-workout-move="2"]');
  const visualVideoInDetail=await page.$('video.pushup-real-video');
  const preview=await page.$eval('video.pushup-real-video',e=>({src:e.getAttribute('src'),poster:e.poster}));
  await page.click('#guide-next');
  const squat=await page.evaluate(()=>({
    name:document.querySelector('.work-title')?.textContent,
    schematic:!!document.querySelector('svg.moving-figure'),
    video:!!document.querySelector('video.motion-video'),
    label:document.querySelector('.motion-badge')?.textContent
  }));
  await page.click('#guide-home');
  await page.click('#workout-detail-start');
  await page.evaluate(()=>{const now=Date.now.bind(Date);Date.now=()=>now()+78000;});
  await new Promise(r=>setTimeout(r,450));
  const player=await page.evaluate(()=>({
    title:document.getElementById('exercise-name')?.textContent,
    previewSrc:document.querySelector('video.pushup-real-video')?.getAttribute('src'),
    video:!!document.querySelector('video.motion-video')
  }));
  await page.screenshot({path:'/tmp/utro7-g1-blocked-instruction.png'});
  const result={
    policy,preview,squat,player,visualVideoInDetail:!!visualVideoInDetail,errors
  };
  console.log(JSON.stringify(result,null,2));
  await browser.close();
  if(!policy||policy.count!==9||policy.published!==0||policy.pushupWoman!=='rejected'||
     policy.marchWoman!=='prototype'||!preview.src.includes('male-pushup-approved-visual.mp4')||!visualVideoInDetail||
     !squat.schematic||squat.video||!squat.label.includes('не проверена')||
     player.title!=='Отжимания'||!player.previewSrc?.includes('male-pushup-approved-visual.mp4')||!player.video||errors.length)process.exitCode=1;
})().catch(err=>{console.error('QA_ERROR',err.stack);process.exitCode=2});
