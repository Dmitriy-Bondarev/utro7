// GENERATED: content/motion/registry.json — edit JSON, not this file.
(function (root) {
  'use strict';
  const registry = {"schemaVersion":1,"publicationRule":"Only approved assets with reviewer, review date, device QA and checksum may play as exercise instruction.","assets":[{"exerciseId":"march","trainerId":"woman","rigId":"geometric-v1","status":"prototype","reason":"Unvalidated geometric animation","video":"./assets/motion/v1/woman-march.mp4","poster":"./assets/motion/v1/woman-march.jpg","review":null},{"exerciseId":"march","trainerId":"man","rigId":"geometric-v1","status":"prototype","reason":"Unvalidated geometric animation","video":"./assets/motion/v1/man-march.mp4","poster":"./assets/motion/v1/man-march.jpg","review":null},{"exerciseId":"squat","trainerId":"woman","rigId":"geometric-v1","status":"prototype","reason":"Unvalidated geometric animation","video":"./assets/motion/v1/woman-squat.mp4","poster":"./assets/motion/v1/woman-squat.jpg","review":null},{"exerciseId":"squat","trainerId":"man","rigId":"geometric-v1","status":"prototype","reason":"Unvalidated geometric animation","video":"./assets/motion/v1/man-squat.mp4","poster":"./assets/motion/v1/man-squat.jpg","review":null},{"exerciseId":"pushup","trainerId":"woman","rigId":"geometric-v1","status":"rejected","reason":"Rejected: erroneous limb motion, no technique validation","video":"./assets/motion/v1/woman-pushup.mp4","poster":"./assets/motion/v1/woman-pushup.jpg","review":null},{"exerciseId":"pushup","trainerId":"man","rigId":"geometric-v1","status":"rejected","reason":"Rejected: erroneous limb motion, no technique validation","video":"./assets/motion/v1/man-pushup.mp4","poster":"./assets/motion/v1/man-pushup.jpg","review":null},{"exerciseId":"pushup","trainerId":"trainer_female_01","rigId":"mpfb-game-engine-53-bones","status":"rejected","reason":"Inverted elbows/forearms in user review; replace poses and retest","video":"./assets/motion/quality-v2/female-pushup.mp4","poster":"./assets/motion/quality-v2/female-pushup-poster.jpg","source":"./assets/motion/quality-v2/trainer-female-pushup.blend","review":null},{"exerciseId":"pushup","trainerId":"trainer_female_01","rigId":"mpfb-game-engine-53-bones-g2-v1","status":"review","reason":"96-frame 30fps H.264 candidate, 12/12 geometric checks pass; visual/fitness professional/iPhone acceptance pending.","video":"./assets/motion/quality-g2/female-pushup-candidate.mp4","poster":"./assets/motion/quality-g2/female-pushup-candidate-poster.jpg","source":"./assets/motion/quality-g2/trainer-female-pushup-motion-candidate.blend","reviewPage":"./preview/pushup-g2/","review":null},{"exerciseId":"squat","trainerId":"trainer_female_01","rigId":"mpfb-game-engine-53-bones-squat-g1","status":"review","reason":"Full 120-frame squat 3D candidate. 9/9 heuristic geometry tests passed; user/fitness expert/iPhone review not completed.","video":"./assets/motion/squat-g1/female-squat-candidate.mp4","poster":"./assets/motion/squat-g1/female-squat-poster.jpg","sourceGenerator":"tools/blender/build_squat_g1.py","reviewPage":"./preview/squat-g1/","review":null}]};
  const required = ['techniqueApproved','visualApproved','iphoneApproved','rightsChecked'];
  function approved(entry) {
    const review = entry && entry.review;
    return !!(entry && entry.status === 'approved' && review &&
      required.every(key => review[key] === true) &&
      typeof review.reviewer === 'string' && review.reviewer.trim() &&
      typeof review.reviewedAt === 'string' && review.reviewedAt.trim() &&
      /^[0-9a-f]{64}$/i.test(entry.sha256 || ''));
  }
  const api = {
    schemaVersion: registry.schemaVersion,
    getApproved(exerciseId, trainerId) {
      return registry.assets.find(asset => asset.exerciseId === exerciseId &&
        asset.trainerId === trainerId && approved(asset)) || null;
    },
    getStatus(exerciseId, trainerId) {
      const found = registry.assets.filter(asset => asset.exerciseId === exerciseId && asset.trainerId === trainerId);
      return found.some(item => item.status === 'rejected') ? 'rejected' :
        found.some(item => item.status === 'review') ? 'review' :
        found.some(item => item.status === 'prototype') ? 'prototype' : 'not_produced';
    },
    all() { return registry.assets.map(item => ({...item})); }
  };
  root.Utro7MotionPolicy = Object.freeze(api);
})(typeof window === 'undefined' ? globalThis : window);
