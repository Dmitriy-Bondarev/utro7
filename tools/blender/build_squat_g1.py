"""Utro7 EX-04: ONE female Blender avatar, ONE bodyweight squat.

Generate 3D working pose candidates from the previously developed MPFB female
rig. The full motion stays under review until user/fitness specialist acceptance.
Avoids switching to schematic SVG or producing extra trainers/exercises.

blender -b -t 6 -P tools/blender/build_squat_g1.py
"""
import bpy
from pathlib import Path
from mathutils import Vector
import math

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"assets"/"motion"/"squat-g1"
OUT.mkdir(parents=True,exist_ok=True)
FRAMES=OUT/"_frames"
FRAMES.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"assets/motion/quality-v3/trainer-female-pushup-static-v3.blend"))
scene=bpy.context.scene
rig=next(o for o in bpy.data.objects if o.type=="ARMATURE")
rig.name="Utro7 Female Instructor - Squat Candidate"
rig.animation_data_clear()
rig.rotation_mode="XYZ"
rig.rotation_euler=(0,0,0)
rig.location=(0,0,0)
rig.scale=(1,1,1)
for bone in rig.pose.bones:
    bone.rotation_mode='XYZ'
    bone.rotation_euler=(0,0,0)
    bone.location=(0,0,0)
    bone.scale=(1,1,1)
    for constraint in list(bone.constraints):
        if constraint.type=='IK':
            bone.constraints.remove(constraint)
for ob in list(bpy.data.objects):
    if ob.name.startswith(("WristLock_","ElbowPole_")):
        bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.view_layer.update()  # flush source plank rig world transforms before calculating rest ankles

# Standing whole body, feet grounded. A 2-bone IK chain locks ankle roots,
# while knee pole targets prescribe anatomical forward knee flexion.
leg_goals={}
for side in ("l","r"):
    bone=rig.data.bones["calf_"+side]
    ankle=rig.matrix_world @ bone.tail_local
    knee=rig.matrix_world @ rig.data.bones["thigh_"+side].tail_local
    bpy.ops.object.empty_add(type="SPHERE",location=ankle)
    goal=bpy.context.object
    goal.name="SquatAnkleLock_"+side
    goal.empty_display_size=.04
    bpy.ops.object.empty_add(type="SPHERE",location=(knee.x,-.65,knee.z))
    pole=bpy.context.object
    pole.name="SquatKneePole_"+side
    pole.empty_display_size=.035
    ik=rig.pose.bones["calf_"+side].constraints.new('IK')
    ik.name="Squat: knee bends forward, ankle fixed"
    ik.target=goal
    ik.chain_count=2
    ik.use_stretch=False
    ik.pole_target=pole
    ik.pole_angle=0.0
    leg_goals[side]=(goal,pole)
    print("SQUAT_ANKLE",side,tuple(round(c,3) for c in ankle),"KNEE",tuple(round(c,3) for c in knee),flush=True)

# Keep both shoes pointing forward and flat while the calf rotates. A two-bone
# ankle IK alone does NOT keep foot orientation (the previous candidate had
# 12 cm of toe sliding and 11 cm penetration into the ground).
bpy.context.view_layer.update()
for side in ("l","r"):
    pb=rig.pose.bones["foot_"+side]
    target_rot=(rig.matrix_world @ pb.matrix).to_quaternion()
    bpy.ops.object.empty_add(type="ARROWS",location=(1.5 if side=="l" else -1.5,0,.05))
    anchor=bpy.context.object
    anchor.name="SquatFootOrientationLock_"+side
    anchor.rotation_mode="QUATERNION"
    anchor.rotation_quaternion=target_rot
    anchor.empty_display_size=.06
    con=pb.constraints.new('COPY_ROTATION')
    con.name="Keep sole parallel to ground"
    con.target=anchor
    con.owner_space='WORLD'
    con.target_space='WORLD'
    con.mix_mode='REPLACE'
    con.influence=1.0

# Bodyweight squat: hip center goes back as it goes down. Upright torso
# leans forward slightly in deep squat to maintain plausible balance.
# The knees are resolved by the IK leg chains, not hand-rotated.
# One controlled full cycle, 4.0s @30fps.
timeline=[
    ("P0",1,0.00), ("P1",18,.22), ("P2",34,.52),
    ("P3",51,1.00), ("P3_hold",58,1.00),
    ("P4",86,.50), ("P5",111,0.00), ("P5_hold",121,0.00)
]
spine=rig.pose.bones["spine_01"]
spine.rotation_mode="XYZ"
# Arms are lifted for balance. Original resting pose has relaxed bent elbows;
# upward/forward pose is modest to avoid shoulder overextension.
for frame_name,frame,d in timeline:
    rig.location=(0,.19*d,-.33*d)
    rig.keyframe_insert(data_path="location",frame=frame,group="Squat: center of mass")
    spine.rotation_euler=(.16*d,0,0)
    spine.keyframe_insert(data_path="rotation_euler",frame=frame,group="Squat: torso")
    for side in ("l","r"):
        arm=rig.pose.bones["upperarm_"+side]
        arm.rotation_mode="XYZ"
        arm.rotation_euler=(.12*d,0,0)
        arm.keyframe_insert(data_path="rotation_euler",frame=frame,group="Squat: arms balance")

scene.frame_start=1
scene.frame_end=120
scene.render.fps=30
scene.frame_set(1)
rig["exerciseId"]="squat"
rig["reviewStatus"]="CANDIDATE_NOT_APPROVED"
rig["trainerId"]="trainer_female_01"
rig["notes"]="Needs 3-view motion anatomy and independent training technique review"
for name in ("Push-up side camera","G1 Pose Review A_side","G1 Pose Review B_three_quarter","G1 Pose Review C_front"):
    if name in bpy.data.objects:bpy.data.objects[name].hide_render=True

def aim_at(camera,point):
    direction=Vector(point)-camera.location
    camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()

for name,location,view,scale in [
    ("SquatSide",(4,-.9,1.8),(0,0,.84),2.35),
    ("SquatThreeQuarter",(3,-4,1.95),(0,0,.84),2.28),
    ("SquatFront",(0,-5.0,1.85),(0,0,.84),2.35)
]:
    bpy.ops.object.camera_add(location=location)
    cam=bpy.context.object
    cam.name=name
    cam.data.type="ORTHO"
    cam.data.ortho_scale=scale
    aim_at(cam,view)
scene.camera=bpy.data.objects["SquatThreeQuarter"]
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=800
scene.render.resolution_y=800
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"

# Save native source and 3 diagnostic poses, no video until geometry review.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"trainer-female-squat-candidate.blend"))
for camera_name in ("SquatSide","SquatThreeQuarter","SquatFront"):
    scene.camera=bpy.data.objects[camera_name]
    for name,frame in (("P0",1),("P3",51)):
        scene.frame_set(frame)
        scene.render.filepath=str(FRAMES/(camera_name+"_"+name+".png"))
        bpy.ops.render.render(write_still=True)
        print("SQUAT_POSE",camera_name,name,flush=True)
print("SQUAT_G1_DONE",flush=True)
