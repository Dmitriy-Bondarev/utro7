"""One rigged female trainer / one push-up exercise. Authoring prototype.
Run: blender -b -t 6 -P tools/blender/create_pushup_trainer.py
MPFB 2.0.18 extension, CC0 MakeHuman system assets installed locally.
"""
import bpy, math, sys, traceback
from pathlib import Path
from mathutils import Vector, Quaternion
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.entities.objectproperties import HumanObjectProperties
from bl_ext.user_default.mpfb.services.targetservice import TargetService

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"assets"/"motion"/"quality-v2"
OUT.mkdir(parents=True,exist_ok=True)
PACK=Path('/Users/continuum/Library/Application Support/Blender/5.3/extensions/.user/user_default/mpfb/data')

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
human=HumanService.create_human()
human.name="Utro7 · trainer 01 · anatomically proportioned body"
for key,val in {"gender":1.0,"muscle":0.65,"weight":0.40,"age":0.33,"height":0.57}.items():
    HumanObjectProperties.set_value(key,val,entity_reference=human)
TargetService.reapply_macro_details(human)

skin=PACK/"skins/young_caucasian_female/young_caucasian_female.mhmat"
if skin.exists():
    try:
        HumanService.set_character_skin(str(skin),human,skin_type="GAMEENGINE")
        print("SKIN_OK",flush=True)
    except Exception:
        traceback.print_exc()

rig=HumanService.add_builtin_rig(human,"game_engine")
rig.name="Utro7 Push-up Humanoid Rig 53 bones"

for folder,filename,asset_type in [
  ("clothes/female_sportsuit01","female_sportsuit01.mhclo","Clothes"),
  ("hair/ponytail01","ponytail01.mhclo","Hair"),
  ("eyes/low-poly","low-poly.mhclo","Eyes"),
  ("eyebrows/eyebrow001","eyebrow001.mhclo","Eyebrows"),
  ("clothes/shoes01","shoes01.mhclo","Clothes")
]:
    candidate=PACK/folder/filename
    if candidate.is_file():
        try:
            item=HumanService.add_mhclo_asset(str(candidate),human,asset_type=asset_type,material_type="GAMEENGINE")
            print("ASSET_OK",asset_type,filename,str(item),flush=True)
        except Exception as e:print("ASSET_FAIL",filename,str(e),flush=True);traceback.print_exc()
    else: print("ASSET_MISSING",filename,flush=True)

# Fix camera and studio lighting for side-view demonstration.
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.386
    return m

bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005))
floor=bpy.context.object;floor.name="matte studio floor";floor.data.materials.append(material("studio soft gray",(.77,.80,.84)))
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=900
scene.render.resolution_y=600
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.file_format='PNG'
scene.render.fps=20
scene.render.film_transparent=False
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.75,.79,.84,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.38
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"

def aim_at(o,pos):
    direction=Vector(pos)-o.location
    o.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(4.5,-.80,1.85))
cam=bpy.context.object;cam.name="Push-up side camera"
aim_at(cam,(0,-.84,.46))
cam.data.type="ORTHO"
cam.data.ortho_scale=2.84
scene.camera=cam

for name,loc,power,size in [
    ("key softbox",(2.1,-2.4,4.2),300,4.5),
    ("front softbox",(-3.0,-1.5,3.4),170,3.4),
    ("rim light",(-1.2,2.0,3.7),260,3.3)
]:
    bpy.ops.object.light_add(type="AREA",location=loc)
    lamp=bpy.context.object;lamp.name=name;lamp.data.energy=power;lamp.data.shape="DISK";lamp.data.size=size
    aim_at(lamp,(0,-.8,.55))

# Turn a standing rig into a plank (Z-up -> X-forward, slope pivots about toes).
rig.rotation_mode="XYZ"
rig.location=(0,0,.06)
rig.rotation_euler=(1.33,0,0)

targets={}
for side in ('l','r'):
    sign=1 if side=='l' else -1
    bpy.ops.object.empty_add(type='SPHERE',location=(.275*sign,-1.15,.055))
    wrist=bpy.context.object;wrist.name='WristLock_'+side;wrist.empty_display_size=.035
    bpy.ops.object.empty_add(type='SPHERE',location=(.54*sign,-.96,.28))
    pole=bpy.context.object;pole.name='ElbowPole_'+side;pole.empty_display_size=.03
    pb=rig.pose.bones["lowerarm_"+side]
    ik=pb.constraints.new('IK')
    ik.name="Wrist floor contact / 2-bone IK"
    ik.target=wrist;ik.chain_count=2;ik.use_stretch=False
    ik.pole_target=pole;ik.pole_angle=0
    targets[side]=(wrist,pole)

def set_pose(frame,phase):
    angle=1.33 + .14*phase
    rig.rotation_euler=(angle,0,0)
    rig.keyframe_insert(data_path="rotation_euler",frame=frame)
    for side,(wrist,pole) in targets.items():
        wrist.keyframe_insert(data_path="location",frame=frame)
        pole.keyframe_insert(data_path="location",frame=frame)

for frame,phase in ((1,0),(6,.5),(11,1),(16,.5),(21,0),(26,.5),(31,1),(36,.5),(41,0)):
    set_pose(frame,phase)
scene.frame_start=1;scene.frame_end=40
scene.frame_set(1)
bpy.context.view_layer.update()
for side in ('l','r'):
    pb=rig.pose.bones['lowerarm_'+side]
    tail=rig.matrix_world@pb.tail
    head=rig.matrix_world@pb.head
    print("ARM_POSITION",side,"head",tuple(round(x,3) for x in head),"wrist",tuple(round(x,3) for x in tail),"target",tuple(round(x,3) for x in targets[side][0].location),flush=True)
try:
    bpy.ops.file.pack_all()
except Exception as e:print("PACK_WARNING",str(e),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'trainer-female-pushup.blend'))
print("SCENE_WRITTEN",flush=True)

# Render three key poses for inspection before producing any animation.
for frame,filename in [(1,'pushup-top.png'),(11,'pushup-low.png'),(21,'pushup-top2.png')]:
    scene.frame_set(frame)
    scene.render.filepath=str(OUT/filename)
    bpy.ops.render.render(write_still=True)
    print("FRAME_WRITTEN",str(scene.render.filepath),flush=True)
