"""T1 VISUAL REVIEW ONLY — one male Human Generator trial model, no exercises.

Use only private licensed trial for a preliminary user review.
Outputs remain private until vendor license rights are confirmed.
"""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
PRIVATE=ROOT/"assets/trainer_master/private/humgen_trial"
SOURCE=PRIVATE/"humgen_male_trial_visual_candidate.blend"
STUDIO=ROOT/"assets/trainer_master/scenes/utro7_studio_template.blend"
OUT=PRIVATE/"male_review"
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(STUDIO))
scene=bpy.context.scene
dest=bpy.data.collections["TRAINER_MASTER_IMPORT_HERE"]
with bpy.data.libraries.load(str(SOURCE),link=False) as (src,data):
 data.objects=list(src.objects)
objects=[ob for ob in data.objects if ob and ob.type in ("MESH","ARMATURE","CURVES","CURVE")]
for ob in objects:
 if not ob.users_collection: dest.objects.link(ob)
rig=next(ob for ob in objects if ob.type=="ARMATURE")
meshes=[ob for ob in objects if ob.type=="MESH"]
bpy.context.view_layer.update()
pts=[ob.matrix_world@Vector(p) for ob in meshes for p in ob.bound_box]
bounds=[(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)]
print("MALE_RENDER_SOURCE_BOUNDS",bounds,flush=True)
# Person already in native metric origin; no cosmetic mirroring.
assert 1.5<bounds[2][1]-bounds[2][0]<2.2
scene.render.engine="CYCLES"
scene.cycles.samples=28
scene.cycles.use_denoising=True
scene.render.resolution_x=750
scene.render.resolution_y=1125
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene["utro7_asset_id"]="trainer_male_master_candidate_01"
scene["production_stage"]="T1_PRIVATE_TRIAL_VISUAL_REVIEW"
scene["visual_accepted"]=False
scene["not_for_commercial_distribution"]=True
scene["trial_only_male"]=True
scene["wardrobe"]="Provisional trial sweater/jeans; NOT sportswear, cannot pass final acceptance"
scene.camera=bpy.data.objects["RV_03_THREE_QUARTER_FULL"]
bpy.ops.wm.save_as_mainfile(filepath=str(PRIVATE/"male_studio_candidate.blend"))
for name in ("RV_01_FRONT_FULL","RV_02_SIDE_FULL","RV_03_THREE_QUARTER_FULL","RV_04_FACE_CLOSEUP","RV_05_HANDS_CLOSEUP","RV_06_FEET_SHOES_CLOSEUP","RV_07_TORSO_CLOTHING"):
 scene.camera=bpy.data.objects[name]
 scene.render.filepath=str(OUT/(name+".png"))
 bpy.ops.render.render(write_still=True)
 print("MALE_RENDER_OK",name,flush=True)
print("MALE_REVIEW_RENDER_DONE",flush=True)
