import * as THREE from 'three';
import { OrbitControls } from './vendor/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/loaders/GLTFLoader.js';

const root = document.querySelector('#stage');
const status = document.querySelector('#status');
const poseBar = document.querySelector('#pose');
const playButton = document.querySelector('#playPause');
const speedButton = document.querySelector('#speed');
const filePicker = document.querySelector('#modelFile');

const scene = new THREE.Scene();
scene.background = new THREE.Color('#d9e0e4');
scene.fog = new THREE.Fog('#d9e0e4', 5, 10);
const camera = new THREE.PerspectiveCamera(39, 1, .04, 50);
camera.position.set(2.65, 1.63, -2.5);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
renderer.setSize(1, 1, false);
renderer.domElement.style.width = '100%';
renderer.domElement.style.height = '100%';
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.45;
root.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, .43, .05);
controls.enableDamping = true;
controls.dampingFactor = .1;
controls.minDistance = 1.25;
controls.maxDistance = 6;
controls.maxPolarAngle = Math.PI / 2.07;
controls.update();

scene.add(new THREE.HemisphereLight('#ffffff', '#a5b2c1', 2.1));
const key = new THREE.DirectionalLight('#fff6e9', 3.1);
key.position.set(-2, 5, -3);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: .1, far: 14 });
key.shadow.bias = -.0002;
scene.add(key);
const rim = new THREE.DirectionalLight('#e0efff', 1.4);
rim.position.set(4, 3, 4);
scene.add(rim);
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(100, 100),
  new THREE.MeshStandardMaterial({ color: '#d8e0e2', roughness: .94 })
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);
const grid = new THREE.GridHelper(5.0, 10, '#92aaba', '#b9c8ce');
grid.position.y = .003;
grid.material.opacity = .18;
grid.material.transparent = true;
scene.add(grid);

const blue = new THREE.MeshStandardMaterial({ color: '#2464be', roughness: .81 });
const blueTrim = new THREE.MeshStandardMaterial({ color: '#488ae2', roughness: .76 });
const shorts = new THREE.MeshStandardMaterial({ color: '#2e3440', roughness: .88 });
const sole = new THREE.MeshStandardMaterial({ color: '#dee6eb', roughness: .9 });
const shoes = new THREE.MeshStandardMaterial({ color: '#28384a', roughness: .68 });
const skin = new THREE.MeshStandardMaterial({ color: '#d5a78b', roughness: .87 });
const hair = new THREE.MeshStandardMaterial({ color: '#302722', roughness: .97 });
const iris = new THREE.MeshStandardMaterial({ color: '#33475d', roughness: .8 });
const lips = new THREE.MeshStandardMaterial({ color: '#a46d62', roughness: .85 });
const geomBall = new THREE.SphereGeometry(1, 18, 14);

const demo = new THREE.Group();
scene.add(demo);
function ball(parent, material, dimensions) {
  const mesh = new THREE.Mesh(geomBall, material);
  mesh.scale.set(...dimensions);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}
function rod(parent, material, radius) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, 1, 14), material);
  mesh.castShadow = true;
  parent.add(mesh);
  return mesh;
}
const vec = (x, y, z) => new THREE.Vector3(x, y, z);
const midpoint = (a, b) => a.clone().add(b).multiplyScalar(.5);
const up = vec(0, 1, 0);
function positionRod(rodObject, a, b) {
  const direction = b.clone().sub(a);
  rodObject.position.copy(midpoint(a, b));
  rodObject.quaternion.setFromUnitVectors(up, direction.clone().normalize());
  rodObject.scale.y = direction.length();
}

const torso = ball(demo, blue, [.265, .185, .46]);
const chest = ball(demo, blue, [.28, .195, .21]);
const hips = ball(demo, shorts, [.23, .185, .205]);
const neck = ball(demo, skin, [.072, .09, .09]);
const head = ball(demo, skin, [.135, .155, .135]);
const hairCap = ball(demo, hair, [.14, .09, .14]);
const eyes = [-1, 1].map(() => ball(demo, iris, [.014, .012, .01]));
const mouth = ball(demo, lips, [.036, .008, .008]);
const arms = [-1, 1].map(() => ({
  upper: rod(demo, skin, .072),
  forearm: rod(demo, skin, .058),
  sleeve: rod(demo, blue, .085),
  elbow: ball(demo, skin, [.075, .065, .075]),
  wrist: ball(demo, skin, [.063, .04, .07]),
  palm: ball(demo, skin, [.082, .026, .12])
}));
const legs = [-1, 1].map(() => ({
  upper: rod(demo, shorts, .111),
  lower: rod(demo, skin, .079),
  knee: ball(demo, skin, [.088, .076, .088]),
  shoe: ball(demo, shoes, [.095, .067, .17]),
  sole: ball(demo, sole, [.102, .022, .18])
}));

// Animated 3D *mechanical stand-in*, built entirely from original primitives.
// No Human Generator/third-party meshes, textures or rig data are embedded.
function setPose(depth) {
  depth = Math.max(0, Math.min(1, depth));
  const shoulderY = .74 - .37 * depth;
  const pelvisY = .74 - .36 * depth;
  torso.position.set(0, (shoulderY + pelvisY) / 2, -.095);
  chest.position.set(0, shoulderY, -.44);
  hips.position.set(0, pelvisY, .33);
  neck.position.set(0, shoulderY + .035, -.595);
  head.position.set(0, shoulderY + .012, -.82);
  hairCap.position.set(0, shoulderY + .122, -.81);
  eyes.forEach((item, i) => item.position.set((i ? 1 : -1) * .066, shoulderY + .045, -.944));
  mouth.position.set(0, shoulderY - .043, -.954);
  for (let i = 0; i < 2; i++) {
    const side = i === 0 ? -1 : 1;
    const shoulder = vec(side * .245, shoulderY, -.455);
    const elbow = vec(side * (.31 + .125 * depth), .395 - .142 * depth, -.56 + .07 * depth);
    const wrist = vec(side * .345, .101, -.69);
    const arm = arms[i];
    positionRod(arm.upper, shoulder, elbow);
    positionRod(arm.forearm, elbow, wrist);
    const sleeveEnd = shoulder.clone().lerp(elbow, .27);
    positionRod(arm.sleeve, shoulder, sleeveEnd);
    arm.elbow.position.copy(elbow);
    arm.wrist.position.copy(wrist);
    arm.palm.position.set(side * .345, .035, -.76);
    const thighTop = vec(side * .168, pelvisY, .32);
    const knee = vec(side * .17, .465 - .165 * depth, .91);
    const ankle = vec(side * .17, .12, 1.45);
    positionRod(legs[i].upper, thighTop, knee);
    positionRod(legs[i].lower, knee, ankle);
    legs[i].knee.position.copy(knee);
    legs[i].shoe.position.set(side * .17, .091, 1.56);
    legs[i].sole.position.set(side * .17, .031, 1.56);
  }
}

const clock = new THREE.Clock();
let playing = false, speed = 1, phase = 0, localMixer = null, loadedModel = null;
const speedValues = [.5, 1, 1.5];
let speedIndex = 1;
setPose(0);
const setStatus = msg => { status.textContent = msg; };
setStatus('Проверочный 3D-макет готов. Вращай камеру и запускай движение; реальная 3D-модель ещё проходит подготовку.');
function togglePlay() {
  playing = !playing;
  playButton.textContent = playing ? '❚❚ Пауза' : '▶ Запустить';
  playButton.setAttribute('aria-pressed', String(playing));
}
playButton.onclick = togglePlay;
speedButton.onclick = () => {
  speedIndex = (speedIndex + 1) % speedValues.length;
  speed = speedValues[speedIndex];
  speedButton.textContent = 'Скорость ' + speed + '×';
};
poseBar.oninput = event => {
  if (playing) togglePlay();
  const v = Number(event.target.value) / 100;
  phase = Math.acos(1 - 2 * v) / Math.PI;
  if (!loadedModel) setPose(v);
  else if (localMixer) localMixer.setTime(v * (loadedModel.animations?.[0]?.duration || 1));
};
const cameraPresets = {
  side: [3.5, 1.42, .3],
  front: [0, 1.42, -3.2],
  threeQuarter: [2.4, 1.83, -2.6],
  opposite: [-3.3, 1.45, .3]
};
document.querySelectorAll('[data-camera]').forEach(button => {
  button.onclick = () => {
    camera.position.set(...cameraPresets[button.dataset.camera]);
    controls.target.set(0, .46, .15);
    controls.update();
    document.querySelectorAll('[data-camera]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  };
});
document.querySelector('#resetCamera').onclick = () => {
  camera.position.set(...cameraPresets.threeQuarter);
  controls.target.set(0, .46, .15);
  controls.update();
};
document.querySelector('#resetModel').onclick = () => {
  if (loadedModel) {
    scene.remove(loadedModel.scene);
    loadedModel = null;
    localMixer = null;
  }
  demo.visible = true;
  playing = false;
  playButton.textContent = '▶ Запустить';
  phase = 0;
  poseBar.value = '0';
  setPose(0);
  setStatus('Проверочный 3D-манекен: поворот, пауза и движение доступны. Это не финальная реалистичная модель.');
  filePicker.value = '';
};

// Uploads are kept inside this browser session only: never sent to a server.
filePicker.addEventListener('change', event => {
  const file = event.target.files?.[0];
  if (!file) return;
  if (!/\.glb$/i.test(file.name)) {
    setStatus('Нужен .glb с подходящими правами. Файл не загружен.'); return;
  }
  const url = URL.createObjectURL(file);
  new GLTFLoader().load(url, asset => {
    URL.revokeObjectURL(url);
    if (loadedModel) scene.remove(loadedModel.scene);
    loadedModel = asset;
    demo.visible = false;
    const bounds = new THREE.Box3().setFromObject(asset.scene);
    const size = bounds.getSize(new THREE.Vector3());
    if (!Number.isFinite(size.length()) || size.length() === 0) {
      loadedModel = null; demo.visible = true;
      setStatus('Неверная 3D-геометрия, технический макет восстановлен.'); return;
    }
    const factor = 1.9 / Math.max(size.x, size.y, size.z);
    asset.scene.scale.setScalar(factor);
    const scaledBox = new THREE.Box3().setFromObject(asset.scene);
    const center = scaledBox.getCenter(new THREE.Vector3());
    asset.scene.position.sub(center);
    asset.scene.position.y += scaledBox.getSize(new THREE.Vector3()).y * .5;
    scene.add(asset.scene);
    asset.scene.traverse(obj => { if (obj.isMesh) obj.castShadow = true; });
    localMixer = asset.animations?.length ? new THREE.AnimationMixer(asset.scene) : null;
    if (localMixer) localMixer.clipAction(asset.animations[0]).play();
    playing = false; playButton.textContent = '▶ Запустить';
    setStatus('Локально открыт: ' + file.name + (localMixer ? ' · есть 3D-анимация.' : ' · анимаций нет, доступен только поворот.'));
  }, undefined, err => {
    URL.revokeObjectURL(url);
    setStatus('Не удалось открыть GLB: ' + (err?.message || 'неизвестная ошибка'));
  });
});

function fit() {
  const width = Math.max(1, root.clientWidth);
  const height = Math.max(1, root.clientHeight);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height, false);
}
const observer = new ResizeObserver(fit);
observer.observe(root);
fit();
function tick() {
  const dt = Math.min(clock.getDelta(), .1);
  if (playing) {
    phase += dt * speed / 3.2;
    if (phase > 1) phase -= 1;
    if (loadedModel) {
      if (localMixer) localMixer.update(dt * speed);
    } else {
      const depth = (1 - Math.cos(phase * Math.PI * 2)) / 2;
      setPose(depth);
      poseBar.value = String(Math.round(depth * 100));
    }
  }
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
tick();
window.__utro7Viewer = Object.freeze({
  get cameraControlsReady() { return !!controls; },
  get modelMode() { return loadedModel ? 'user-glb' : 'procedural-skeleton-demo'; },
  get playing() { return playing; },
  get animationReady() { return !!(localMixer || demo); }
});
