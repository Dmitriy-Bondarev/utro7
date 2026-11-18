"""T0 trial: import one CC0 human into the neutral Blender studio.

This is a candidate evaluation only; never mark the trainer as approved.
Usage: blender -b -t 8 -P tools/blender/trainer_master/evaluate_grab3d_woman.py
Licensed source is in an ignored private folder on Mac.
"""
import bpy
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/"assets/trainer_master/private/grab3d-woman-base/woman-base-character-rigged.blend"
STUDIO=ROOT/"assets/trainer_master/scenes/utro7_studio_template.blend"
OUT=ROOT/"assets/trainer_master/renders/grab3d_evaluation"
PRIVATE_SCENE=ROOT/"assets/trainer_master/private/grab3d-woman-base/evaluation-studio.blend"
OUT.mkdir(parents=True,exist_ok=True)
assert SOURCE.is_file() and STUDIO.is_file()
bpy.ops.wm.open_mainfile(filepath=str(STUDIO))
sc=bpy.context.scene
target=bpy.data.collections["TRAINER_MASTER_IMPORT_HERE"]

with bpy.data.libraries.load(str(SOURCE),link=False) as (source,data):
    data.objects=list(source.objects)

objlist=[o for o in data.objects if o and o.type in {"MESH","ARMATURE"}]
assert len([o for o in objlist if o.type=="ARMATURE"])==1
assert len([o for o in objlist if o.type=="MESH"])>=1

for obj in objlist:
    if not obj.users_collection:target.objects.link(obj)
    if obj.animation_data:obj.animation_data_clear()

bpy.context.view_layer.update()
rig=next(o for o in objlist if o.type=="ARMATURE")
rig.data.pose_position="POSE"
for pb in rig.pose.bones:
    pb.matrix_basis.identity()
sc.frame_set(1)
bpy.context.view_layer.update()
print("NEUTRAL_REST_POSE_RESET",len(rig.pose.bones),flush=True)
meshes=[o for o in objlist if o.type=="MESH"]
for ob in meshes:
    print("TRIAL_MODEL",ob.name,len(ob.data.vertices),[i.name for i in ob.data.materials if i],flush=True)

def bounds():
    pts=[]
    for ob in meshes:
        evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        for v in evaluated.bound_box:pts.append(evaluated.matrix_world@Vector(v))
    return (Vector([min(v[i] for v in pts) for i in range(3)]),
            Vector([max(v[i] for v in pts) for i in range(3)]))

mn,mx=bounds()
print("SOURCE_BOUNDS",tuple(round(v,3) for v in mn),tuple(round(v,3) for v in mx),flush=True)
offset=Vector((-(mn.x+mx.x)/2,-(mn.y+mx.y)/2,-mn.z))
rig.location+=offset
bpy.context.view_layer.update()
mn,mx=bounds()
print("ALIGNED_BOUNDS",tuple(round(v,3) for v in mn),tuple(round(v,3) for v in mx),flush=True)
height=mx.z-mn.z
assert 1.1 < height < 2.2,("Unexpected scale",height)

sc["production_stage"]="T0_CANDIDATE_VISUAL_REVIEW"
sc["human_model_loaded"]=True
sc["visual_accepted"]=False
sc["source_asset_license_checked"]=False
sc["source_vendor"]="Grab3D"
sc["source_asset"]="woman-base-character-rigged.blend"
sc["source_notes"]="Publisher CC0; AI-assisted via Meshy. Acceptance pending."
sc.render.engine="CYCLES"
sc.cycles.samples=24
sc.render.resolution_x=900
sc.render.resolution_y=1350
sc.render.resolution_percentage=100
sc.render.image_settings.color_mode="RGB"
sc.camera=bpy.data.objects["RV_03_THREE_QUARTER_FULL"]
bpy.ops.wm.save_as_mainfile(filepath=str(PRIVATE_SCENE))
print("TRIAL_SCENE",PRIVATE_SCENE,flush=True)
for camera_name in ("RV_01_FRONT_FULL","RV_02_SIDE_FULL","RV_03_THREE_QUARTER_FULL","RV_04_FACE_CLOSEUP","RV_05_HANDS_CLOSEUP","RV_06_FEET_SHOES_CLOSEUP","RV_07_TORSO_CLOTHING"):
    sc.camera=bpy.data.objects[camera_name]
    sc.render.filepath=str(OUT/(camera_name+".png"))
    bpy.ops.render.render(write_still=True)
    print("TRIAL_RENDER",camera_name,flush=True)
print("TRIAL_RENDER_COMPLETE",len(objlist),"objects",flush=True)
