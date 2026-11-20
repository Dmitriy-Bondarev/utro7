import * as THREE from 'three';
import {OrbitControls} from '../digital-human-studio/vendor/controls/OrbitControls.js';
import {GLTFLoader} from '../digital-human-studio/vendor/loaders/GLTFLoader.js';
const stage=document.getElementById('stage'),status=document.getElementById('status'),btn=document.getElementById('toggle');
const params=new URLSearchParams(location.search);
const embedded=params.get('embed')==='1';
const trainer=params.get('trainer')==='female'?'female':'male';
const exercise=params.get('exercise')==='squat'?'squat':'pushup';
const source='./trainer_'+trainer+'_'+exercise+'.glb';
if(embedded)document.documentElement.classList.add('embedded');
const scene=new THREE.Scene();scene.background=new THREE.Color('#dce5e6');
const camera=new THREE.PerspectiveCamera(40,1,.05,100);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(300,350);stage.appendChild(renderer.domElement);
renderer.domElement.style.width='100%';renderer.domElement.style.height='100%';
scene.add(new THREE.HemisphereLight(0xffffff,0xa0b4be,2));
const light=new THREE.DirectionalLight('#ffffff',3);light.position.set(3,7,5);scene.add(light);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.1;
const grid=new THREE.GridHelper(8,20,'#a5bac5','#c7d5da');scene.add(grid);
let mixer=null, playing=params.get('paused')!=='1';btn.textContent=playing?'Пауза':'Продолжить';
new GLTFLoader().load(source,g=>{
  const model=g.scene;scene.add(model);model.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());
  status.textContent=(trainer==='female'?'Женский тренер':'Мужской тренер')+' · '+(exercise==='squat'?'Приседания':'Отжимания')+' · '+ 'Загружено: '+size.toArray().map(v=>v.toFixed(2)).join(' × ')+' м. Анимаций: '+g.animations.length+'.';
  model.position.sub(center);model.position.y+=size.y/2;
  const radius=Math.max(size.length()/2,1) * (embedded?.85:1);
  const lookY=exercise==='squat'?size.y*.47:.40;
  camera.position.set(radius*1.55,lookY+radius*.65,radius*1.9);camera.lookAt(0,lookY,0);
  controls.target.set(0,lookY,0);controls.minDistance=.6;controls.maxDistance=radius*8;controls.update();
  if(g.animations.length){mixer=new THREE.AnimationMixer(model);mixer.clipAction(g.animations[0]).play();}
},null,e=>{status.textContent='Ошибка загрузки: '+String(e)});
function fit(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
window.addEventListener('resize',fit);fit();
function setPlaying(value){playing=!!value;btn.textContent=playing?'Пауза':'Продолжить';}
document.getElementById('toggle').onclick=()=>setPlaying(!playing);
window.addEventListener('message',e=>{
 if(e.origin!==location.origin)return;
 if(e.data?.type==='utro7-workout-play')setPlaying(true);
 if(e.data?.type==='utro7-workout-pause')setPlaying(false);
});
for(const [id,xyz] of [['front',[0,1,3]],['side',[3,1,0]],['back',[0,1,-3]],['reset',[2,1.4,2.5]]]){
 document.getElementById(id).onclick=()=>{const r=camera.position.distanceTo(controls.target);camera.position.set(xyz[0]*r/3,controls.target.y+xyz[1]*r/3,xyz[2]*r/3);controls.update();};
}
let prev=performance.now();
function tick(now){const dt=Math.min((now-prev)/1000,.1);prev=now;if(mixer&&playing)mixer.update(dt);controls.update();renderer.render(scene,camera);requestAnimationFrame(tick);}requestAnimationFrame(tick);
window.__utro7Real3D={get loaded(){return !!mixer},get playing(){return playing},get camera(){return camera},get modelType(){return 'cc0-sportswear-not-approved'},get trainer(){return trainer},get exercise(){return exercise}};
