"""Build ONE controlled G2 push-up animation candidate from reviewed-instrumented G1 rig.

Never marks the exercise as approved and never replaces the main app player.
Human trainer requires user + fitness specialist review before instructional release.

Run: blender -b -t 6 -P tools/blender/build_pushup_motion_candidate.py
Then: blender -b -t 6 -P tools/blender/render_pushup_motion_candidate.py
"""
import bpy
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"assets/motion/quality-v3/trainer-female-pushup-static-v3.blend"
OUT=ROOT/"assets/motion/quality-g2"
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE))
scene=bpy.context.scene
rig=next(o for o in bpy.data.objects if o.type=="ARMATURE")

# Production candidate motion from a single physically continuous root motion path.
# One full eccentric/concentric repetition takes ~3.2s at 30fps.
# Rig bones remain IK-constrained to the fixed palm targets throughout.
rig.animation_data_clear()
rig.rotation_mode="XYZ"
rig.location.z=0.205
for side in ("l","r"):
    pb=rig.pose.bones["lowerarm_"+side]
    ik=next(c for c in pb.constraints if c.type=="IK")
    ik.pole_angle=-math.pi/2
    ik.use_stretch=False
    target=bpy.data.objects["WristLock_"+side]
    target.animation_data_clear()  # targets fixed, no accidental hand slides
    pole=bpy.data.objects["ElbowPole_"+side]
    pole.animation_data_clear()

# Smooth, deliberate one-repetition loop. P0 and P5 match.
pose_timeline=[
    ("P0", 1, 0.00),    # high plank
    ("P1", 20, 0.25),   # 25% lower
    ("P2", 34, 0.58),   # 58% lower
    ("P3", 47, 1.00),   # bottom
    ("P3_hold",52,1.00),
    ("P4", 70, 0.50),   # halfway up
    ("P5", 90, 0.00),   # fully up
    ("P5_hold",97,0.00)
]
for phase,frame,progress in pose_timeline:
    rig.rotation_euler=(1.33 + 0.14*progress,0,0)
    rig.keyframe_insert(data_path="rotation_euler",frame=frame,group="Pushup One Rep G2")
action=rig.animation_data.action
if action is not None:
    # Blender 5 supports legacy FCurve and layered actions; evaluate correct API.
    fcurves=list(getattr(action,"fcurves",[]))
    if not fcurves:
        slot=rig.animation_data.action_slot
        if slot:
            for layer in action.layers:
                for strip in layer.strips:
                    if hasattr(strip,"channelbag"):
                        bag=strip.channelbag(slot)
                        if bag:
                            fcurves.extend(list(bag.fcurves))
    for curve in fcurves:
        for k in curve.keyframe_points:
            k.interpolation='BEZIER'
            k.handle_left_type='AUTO_CLAMPED'
            k.handle_right_type='AUTO_CLAMPED'

scene.frame_start=1
scene.frame_end=96
scene.frame_set(1)
scene.render.fps=30
scene.render.resolution_x=960
scene.render.resolution_y=600
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.camera=bpy.data.objects["G1 Pose Review A_side"]
rig["motion_revision"]="g2-pushup-96frames-v1"
rig["review_status"]="CANDIDATE_UNAPPROVED"
rig["export_notes"]="Replaces old 2x/2s swing with 1 deliberate rep in 3.2s; awaiting technique review"
rig["reference_exercise"]="content/exercises/EX-03-pushup.ru.json"
bpy.context.view_layer.update()

dest=OUT/"trainer-female-pushup-motion-candidate.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print("UTRO7_G2_SCENE",dest,flush=True)
print("UTRO7_G2_POSE_TIMELINE",pose_timeline,flush=True)
print("UTRO7_G2_VIDEO_FRAMES",scene.frame_start,scene.frame_end,"fps",scene.render.fps,flush=True)
