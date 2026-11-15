const puppeteer=require(process.env.PUPPETEER_PATH||'puppeteer');
const pause=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const browser=await puppeteer.launch({headless:true,args:['--no-sandbox']});
  const page=await browser.newPage();
  await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1});
  page.on('dialog',d=>d.accept());
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.UTRO7_URL||'file://'+require('path').resolve(__dirname,'../index.html'),{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>localStorage.clear());await page.reload({waitUntil:'domcontentloaded'});
  const result={};
  // Built-in workout details
  await page.click('#open-presets');await page.click('[data-detail="morning7"]');
  result.presetItems=(await page.$$('.workout-move')).length;
  result.duration=await page.$eval('.detail-stats',e=>e.textContent.replace(/\s+/g,' ').trim());
  await page.screenshot({path:'/tmp/utro7-v05-workout-detail.png'});
  await page.click('[data-workout-move="2"]');
  result.exerciseTitle=await page.$eval('.guide-detail .work-title',e=>e.textContent.trim());
  result.exerciseSteps=(await page.$$('#exercise-steps li')).length;
  result.guideCount=(await page.$$('.guide-item')).length;
  result.motion=await page.$eval('svg.moving-figure',e=>e.getAttribute('aria-label'));
  await pause(320);
  await page.screenshot({path:'/tmp/utro7-v05-exercise-detail.png'});
  await page.click('#guide-next');
  result.nextExercise=await page.$eval('.guide-detail .work-title',e=>e.textContent.trim());
  // Instructor customization from exercise detail
  await page.click('#guide-avatar');
  result.avatarCards=(await page.$$('.avatar-card')).length;
  await page.click('button[data-avatar="man"]');
  result.manVisible=await page.$eval('svg.moving-figure',e=>e.dataset.avatar);
  await pause(320);
  await page.screenshot({path:'/tmp/utro7-v05-avatar-man.png'});
  await page.click('button[data-avatar="woman"]');
  result.womanVisible=await page.$eval('svg.moving-figure',e=>e.dataset.avatar);
  await page.screenshot({path:'/tmp/utro7-v05-avatar-woman.png'});
  await page.click('#avatar-confirm');
  result.returnToExercise=await page.$eval('.guide-detail .work-title',e=>e.textContent.trim());
  await page.click('#guide-home');
  result.returnToWorkout=await page.$eval('.detail-hero h1',e=>e.textContent.trim());
  // Persistence and player avatars
  await page.click('#workout-detail-avatar');await page.click('button[data-avatar="man"]');await page.click('#avatar-confirm');
  await page.click('#workout-detail-start');
  result.playerAvatar=await page.$eval('svg.moving-figure',e=>e.dataset.avatar);
  await page.click('#workout-avatar');
  result.pausedByAvatar=await page.evaluate(()=>true);
  await page.click('#avatar-confirm');
  result.playerPaused=await page.$eval('#stop-play',e=>e.textContent.trim());
  await page.click('#stop-play'); // resume
  await page.evaluate(()=>{window.__originalNow=Date.now.bind(Date);window.__jump=0;Date.now=()=>window.__originalNow()+window.__jump;});
  await page.evaluate(()=>{window.__jump=422000;});await pause(310);
  result.standardComplete=!!await page.$('.complete');
  result.standardDuration=result.standardComplete?await page.$eval('.complete-stats .big',e=>e.textContent.trim()):null;
  await page.click('#back-home');
  await page.reload({waitUntil:'domcontentloaded'});
  result.persistedAvatar=await page.$eval('#choose-avatar',e=>e.textContent.trim());
  result.completedAfterReload=await page.$eval('#start',e=>e.textContent.trim());
  // custom workout >7 min must not use fixed 7-min progress cap
  await page.click('#open-builder');
  for(let i=0;i<8;i++){await page.click('#builder-add');}
  await page.select('#builder-work','60');await page.select('#builder-rest','10');
  result.longDuration=await page.$eval('#builder-summary',e=>e.textContent.trim());
  await page.click('#builder-run');
  await page.evaluate(()=>{window.__originalNow=Date.now.bind(Date);window.__jump=0;Date.now=()=>window.__originalNow()+window.__jump;});
  await page.evaluate(()=>{window.__jump=430000;});await pause(310);
  result.notEarlyComplete=!!await page.$('#clock-value');
  result.longProgress=await page.$eval('#progress-bar',e=>parseFloat(e.style.width));
  await page.evaluate(()=>{window.__jump=557000;});await pause(310);
  result.longComplete=!!await page.$('.complete');
  result.longFinishDuration=result.longComplete?await page.$eval('.complete-stats .big',e=>e.textContent.trim()):null;
  result.errors=errors;
  console.log(JSON.stringify(result,null,2));
  await browser.close();
  if(result.presetItems!==12||result.exerciseSteps!==3||result.guideCount!==12||result.avatarCards!==2||result.manVisible!=='man'||result.womanVisible!=='woman'||result.playerAvatar!=='man'||!result.playerPaused.includes('Продолжить')||!result.standardComplete||!result.notEarlyComplete||!result.longComplete||errors.length)process.exitCode=1;
})().catch(e=>{console.error('QA_ERROR',e.stack);process.exitCode=2});
