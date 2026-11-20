# 3D Sports Trainer — source, rights, status

**Asset:** `trainer_sports_pushup.glb`, a skinned and animated 3D human with fitted sportswear-color surfaces, used in the rotatable 3D preview embedded in the workout app.

**Human source:** [OpenGym3D](https://github.com/AssiamahS/opengym3d), source `https://assiamahs.github.io/opengym3d/assets/push_up.glb`. Its `assets/ASSET_LIBRARY.json` documents the MakeHuman/MPFB male body as **CC0-1.0**. **Motion:** OpenGym3D's Push-up clip, documented in the same registry as **CC0-1.0**, retargeted from Mesh2Motion / Quaternius Universal Animation Library.

**Local derivation:** Blender 5.3 import (removing a malformed unused glTF morph-weight animation channel solely for Blender importer compatibility), material separation by rest-pose mesh face regions into a blue training jersey, graphite shorts, neutral skin, dark shoes and pale soles, GLB export with full original 163-bone rig and animation intact. The original CC0 GLB is retained locally in the private development workspace, not needed for runtime.

**Important:** No Human Generator Trial 3D mesh, material, texture, or rig was used. The dressed OpenGym3D 3D character differs from the approved 2D video image. This is a visual and technical MVP, NOT accepted as a medically or professionally validated push-up demonstration. Review of hand/foot contacts and body mechanics remains pending.

**QA:** `tests/real3d-sports-integration.cjs` checks actual WebGL frames, pointer rotation, pause/resume, and 2D video fallback using a served app URL.

## November 20 extension — two trainers, two exercises

The viewer accepts `trainer=male|female` and `exercise=pushup|squat` query parameters. Four GLB assets are explicitly versioned: `trainer_male_pushup.glb`, `trainer_female_pushup.glb`, `trainer_male_squat.glb`, `trainer_female_squat.glb`. Hair, eyes, eyebrows, sportswear and footwear are mesh/skin-bound components in each file, not generated 2D images. Female uses a separate native MakeHuman/MPFB CC0 character with 163 bones, retargeted to both original CC0 movement clips by rest-pose bone alignment and baked transformations.

**Quality warning:** this is a visual 3D technology demonstration and not professional or medical instruction. Do not treat joint angles, hand/foot contacts, body geometry or realistic hair/cloth as fully validated. The source Human Generator commercial trial remains excluded.

## MALE-MASTER-CANDIDATE-001 (20 November 2026)

`trainer_male_pushup.glb` replaced with real garment meshes: male polo short-sleeve top, separate shorts, shoes, short messy hair, eyes and eyebrows. OpenGym3D motion retained with local-pose animation transfer, 163 bones. License: CC0 MakeHuman community source assets (Shirts 01, Pants 01, Hair 01 and system assets). Assets were sourced from official MakeHuman CC0 packs; no Human Generator trial content included.

SHA-256 (GLB): `0414f0ed7982d3ae3344392cfa87a5e34841c27769176341701d1477b240f924`. User visual approval pending; motion technique professional review also pending. Not frozen.
