"""Create candidate G1 Blender pose sheet from the rejected MPFB scene.

IMPORTANT: This is an engineering correction, not an approved teaching animation.
One female trainer, one push-up, P0-P5, three review cameras.
No MP4 replacement is published by this script.

Usage: blender -b -t 6 -P tools/blender/repair_pushup_rig_v3.py
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/"assets/motion/quality-v2/trainer-female-pushup.blend"
OUT=ROOT/"assets/motion/quality-v3"
FRAMES=OUT/"_frames"
OUT.mkdir(parents=True,exist_ok=True)
FRAMES.mkdir(parents=True,exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(OLD))
scene=bpy.context.scene
rig=next(o for o in bpy.data.objects if o.type=="ARMATURE")
rig.location.z=0.205  # original .060m produced too-short arms and toes below floor
for side in ("l","r"):
    pb=rig.pose.bones["lowerarm_"+side]
    ik=next(c for c in pb.constraints if c.type=="IK")
    # Same pole angle for this skeleton yields mirrored, outward-and-back elbow flexion.
    ik.pole_angle=-math.pi/2
    ik.use_stretch=False

rig["motion_revision"]="g1-rig-static-v3"
rig["review_status"]="AWAITING_USER_AND_TRAINER_REVIEW"
rig["source_exercise"]="EX-03 pushup"
scene.frame_start=1
scene.frame_end=40
scene.render.resolution_x=720
scene.render.resolution_y=480
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.film_transparent=False


def aim(camera,point):
    direction=Vector(point)-camera.location
    camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()


cameras={
    "A_side":((4.5,-.78,1.72),(0,-.72,.49),2.95),
    "B_three_quarter":((3.0,-3.2,1.82),(0,-.72,.49),2.80),
    "C_front":((0,-4.9,1.56),(0,-.72,.45),2.20)
}
camera_original=scene.camera
camera_objects={}
for name,(loc,target,scale) in cameras.items():
    bpy.ops.object.camera_add(location=loc)
    camera=bpy.context.object
    camera.name="G1 Pose Review "+name
    aim(camera,target)
    camera.data.type="ORTHO"
    camera.data.ortho_scale=scale
    camera_objects[name]=camera

scene.camera=camera_objects["A_side"]
scene.frame_set(1)
bpy.context.view_layer.update()
dest=OUT/"trainer-female-pushup-static-v3.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print("UTRO7_CANDIDATE_SAVED",str(dest),flush=True)
print("UTRO7_FIXED_POLE_ANGLES","left",-math.pi/2,"right",-math.pi/2,"rootZ",rig.location.z,flush=True)

# 6 motion phases × 3 independent cameras for manual review.
phase_frames=[("P0",1),("P1",6),("P2",9),("P3",11),("P4",16),("P5",21)]
for camera_name,camera in camera_objects.items():
    scene.camera=camera
    for label,frame in phase_frames:
        scene.frame_set(frame)
        scene.render.filepath=str(FRAMES/(camera_name+"_"+label+".png"))
        bpy.ops.render.render(write_still=True)
        print("UTRO7_POSE_FRAME",camera_name,label,frame,flush=True)
print("UTRO7_POSE_REVIEW_RENDER_DONE",flush=True)
