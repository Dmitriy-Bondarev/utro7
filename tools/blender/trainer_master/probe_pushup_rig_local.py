"""LOCAL ONLY: trial male Human Generator push-up skeletal feasibility test.

This script never exports / publishes vendor trial 3D meshes. It runs only
inside an authorized Blender trial installation and stores a private .blend.
No fitness instructional approval is implied.
"""
import bpy, math, traceback
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
PRIV=ROOT/'assets/trainer_master/private/humgen_trial'
SRC=PRIV/'humgen_male_trial_visual_candidate.blend'
OUT=PRIV/'motion_lab'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC))
scene=bpy.context.scene
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
assert len(rig.data.bones)>=100
rig.name='Trainer_Lorenzo_3D_Rig'
for pb in rig.pose.bones:
    pb.matrix_basis.identity()
rig.rotation_mode='XYZ'
rig.rotation_euler=(math.pi/2,0,0)
rig.location=(0,0,0.51)
rig.keyframe_insert(data_path='location',frame=1)
# Constraints on existing HG rig: IK wrist and ankle contacts anchored in world.
def target(name,xyz):
    obj=bpy.data.objects.new(name,None)
    scene.collection.objects.link(obj)
    obj.empty_display_type='SPHERE'
    obj.empty_display_size=.065
    obj.location=xyz
    obj.hide_render=True
    return obj
hands={}
feet={}
for side,sign in [('L',1),('R',-1)]:
    h=target('Contact_Hand_'+side,(sign*.34,-1.34,.09))
    pb=rig.pose.bones['forearm.'+side]
    ik=pb.constraints.new('IK')
    ik.name='Utro7_Hand_Contact'
    ik.target=h
    ik.chain_count=2
    ik.use_stretch=False
    hands[side]=h
    f=target('Contact_Ankle_'+side,(sign*.18,-.12,.12))
    pb=rig.pose.bones['shin.'+side]
    ik=pb.constraints.new('IK')
    ik.name='Utro7_Foot_Contact'
    ik.target=f
    ik.chain_count=2
    ik.use_stretch=False
    feet[side]=f
# Animation: straight-arm plank -> descend -> return -> rest hold.
keys=[(1,.51),(13,.38),(22,.30),(29,.30),(40,.38),(52,.51),(61,.51)]
for frame,height in keys:
    rig.location.z=height
    rig.keyframe_insert('location',frame=frame)
    for item in list(hands.values())+list(feet.values()):
        item.keyframe_insert('location',frame=frame)
scene.frame_start=1
scene.frame_end=61
scene.render.fps=24
scene.frame_set(1)
# Floor and background.
mat=bpy.data.materials.new('Utro7_Matte_Floor')
mat.diffuse_color=(.43,.45,.46,1)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.025))
floor=bpy.context.object;floor.name='Review_Floor';floor.data.materials.append(mat)
floor.hide_select=True
def camera(name,location,look,ortho=3.35):
    data=bpy.data.cameras.new(name)
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location=location
    direction=Vector(look)-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=ortho
    return obj
cam_side=camera('Camera_Side_Full',(4.5,-.76,1.15),(0,-.77,.30))
cam_front=camera('Camera_Head_On',(0,-4.8,1.04),(0,-.82,.30))
cam_3q=camera('Camera_ThreeQuarter',(2.8,-3.6,1.5),(0,-.72,.3))
scene.camera=cam_side
for name,loc,power,size in [('Key',(1.5,-1.0,4),750,3),('Fill',(-2,-.2,2.6),400,3.5),('Rim',(1,2,3),500,3)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(Vector((0,-.75,.35))-obj.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1100
scene.render.resolution_y=620
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world.color=(.26,.26,.26)
def worldpt(pb,head=True):
    return rig.matrix_world @ (pb.head if head else pb.tail)
def test_pose(frame):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    hips=worldpt(rig.pose.bones['spine'])
    shoulders=[worldpt(rig.pose.bones['upper_arm.'+side]) for side in ('L','R')]
    wrists=[worldpt(rig.pose.bones['forearm.'+side],False) for side in ('L','R')]
    elbows=[worldpt(rig.pose.bones['forearm.'+side]) for side in ('L','R')]
    ankles=[worldpt(rig.pose.bones['shin.'+side],False) for side in ('L','R')]
    print('POSE_CHECK',frame,'HIP',tuple(round(v,3) for v in hips),'SHOULDERS',[[round(v,3) for v in p] for p in shoulders], 'ELBOWS',[[round(v,3) for v in p] for p in elbows],'WRISTS',[[round(v,3) for v in p] for p in wrists],'ANKLES',[[round(v,3) for v in p] for p in ankles],flush=True)
for f in [1,22,52]:
    test_pose(f)
scene.frame_set(1)
save=OUT/'lorenzo_pushup_rig_trial.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(save))
print('PRIVATE_RIG_SCENE_SAVED',str(save),flush=True)
for frame,camera_obj in [(1,cam_side),(22,cam_side),(1,cam_3q)]:
    scene.frame_set(frame)
    scene.camera=camera_obj
    scene.render.filepath=str(OUT/f'review_{frame:03d}_{camera_obj.name}.png')
    bpy.ops.render.render(write_still=True)
    print('PRIVATE_REVIEW_RENDER',frame,camera_obj.name,flush=True)
print('LOCAL_IK_SCENE_COMPLETE',flush=True)
