#!/usr/bin/env python3
"""Audits the REJECTED MPFB pushup scene. Diagnostics, not an approval tool.

Run:
  blender -b -t 4 assets/motion/quality-v2/trainer-female-pushup.blend \
    -P tools/blender/audit_pushup_rig.py

Output: docs/implementation/rejected_pushup_rig_audit.json

All numeric motion thresholds are pre-review engineering heuristics, not validated
medical/fitness criteria. A PASS does not replace user or specialist review.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
IS_CANDIDATE="quality-v3" in bpy.data.filepath
OUTPUT=ROOT/"docs"/"implementation"/("candidate_pushup_rig_audit.json" if IS_CANDIDATE else "rejected_pushup_rig_audit.json")
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
rig=next(o for o in bpy.data.objects if o.type=="ARMATURE")
scene=bpy.context.scene
frames=[(1,"P0"),(6,"P1"),(9,"P2"),(11,"P3"),(16,"P4"),(21,"P5")]
data=[]


def world(object_, local):
    return object_.matrix_world @ local


def coords(vector):
    return [round(float(x),4) for x in vector]


def pose_bone(armature, name):
    return armature.pose.bones[name]


for frame,label in frames:
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    actual=rig.evaluated_get(dg)
    item={"frame":frame,"phase":label,"arms":{},"feet":{}}
    shoulders=[]
    elbows=[]
    for side in ("l","r"):
        upper=pose_bone(actual,"upperarm_"+side)
        lower=pose_bone(actual,"lowerarm_"+side)
        shoulder=world(actual,upper.head)
        elbow=world(actual,upper.tail)
        wrist=world(actual,lower.tail)
        target=bpy.data.objects["WristLock_"+side].location.copy()
        elbow_angle=math.degrees((shoulder-elbow).angle(wrist-elbow))
        cross=(elbow-shoulder).cross(wrist-elbow)
        signed_bend=float(cross.x)
        shoulder_x=shoulder.x
        item["arms"][side]={
            "shoulder_m":coords(shoulder),
            "elbow_m":coords(elbow),
            "wrist_m":coords(wrist),
            "wrist_target_m":coords(target),
            "wrist_target_error_m":round((wrist-target).length,4),
            "elbow_angle_deg":round(elbow_angle,2),
            "bend_orientation_x":round(signed_bend,4),
            "arm_crosses_centerline": (shoulder_x * wrist.x < -0.0001)
        }
        shoulders.append(shoulder)
        elbows.append(elbow)
        ball=pose_bone(actual,"ball_"+side)
        ball_tip=world(actual,ball.tail)
        item["feet"][side]={"toe_height_m":round(ball_tip.z,4),"toe_m":coords(ball_tip)}
    item["shoulder_height_m"]=round(sum(p.z for p in shoulders)/2,4)
    item["elbow_angle_gap_deg"]=round(abs(item["arms"]["l"]["elbow_angle_deg"]-item["arms"]["r"]["elbow_angle_deg"]),2)
    data.append(item)

errors=[]
top=data[0]
bottom=data[3]
shoulder_drop=round(top["shoulder_height_m"]-bottom["shoulder_height_m"],4)
max_wrist_lock=max(x["wrist_target_error_m"] for row in data for x in row["arms"].values())
max_elbow_gap=max(row["elbow_angle_gap_deg"] for row in data)
max_toe_abs=max(abs(x["toe_height_m"]) for row in data for x in row["feet"].values())
min_elbow_angle=min(x["elbow_angle_deg"] for row in data for x in row["arms"].values())
top_min_elbow_angle=min(x["elbow_angle_deg"] for x in top["arms"].values())
min_toe_height=min(x["toe_height_m"] for row in data for x in row["feet"].values())
max_elbow_y_discrepancy=max(abs((row["arms"]["l"]["elbow_m"][1]-row["arms"]["l"]["shoulder_m"][1])-(row["arms"]["r"]["elbow_m"][1]-row["arms"]["r"]["shoulder_m"][1])) for row in data)
max_elbow_x_mirror_error=max(abs(row["arms"]["l"]["elbow_m"][0]+row["arms"]["r"]["elbow_m"][0]) for row in data)
bend_signs={
    side:{math.copysign(1,row["arms"][side]["bend_orientation_x"])
          for row in data if abs(row["arms"][side]["bend_orientation_x"])>0.0005}
    for side in ("l","r")
}
checks=[
    ("wrist_IK_targets",max_wrist_lock<=0.08,f"max wrist/target delta {max_wrist_lock:.3f}m; heuristic <=0.08m"),
    ("visible_shoulder_lowering",shoulder_drop>=0.09,f"shoulder drop {shoulder_drop:.3f}m; heuristic >=0.09m"),
    ("elbow_left_right_symmetry",max_elbow_gap<=14,f"max elbow angle mismatch {max_elbow_gap:.1f}deg; heuristic <=14deg"),
    ("elbow_angle_not_collapsed",min_elbow_angle>=35,f"min angle {min_elbow_angle:.1f}deg; heuristic >=35deg"),
    ("elbow_bend_no_sign_flip",all(len(s)<=1 for s in bend_signs.values()),f"bend sign sets {bend_signs}"),
    ("hands_no_centerline_crossing",not any(x["arm_crosses_centerline"] for row in data for x in row["arms"].values()),"wrist stays on shoulder side of centerline"),
    ("elbows_bend_toward_feet",min(row["arms"][side]["elbow_m"][1]-row["arms"][side]["shoulder_m"][1] for row in data for side in ("l","r"))>=-0.02,"with face directed -Y, elbows must not fold forward toward head"),
    ("top_elbows_extended",top_min_elbow_angle>=145,f"top elbow angle {top_min_elbow_angle:.1f}deg; expected >=145deg"),
    ("left_right_elbow_sagittal_symmetry",max_elbow_y_discrepancy<=0.09,f"elbow y offset discrepancy {max_elbow_y_discrepancy:.3f}m; expected <=0.09m"),
    ("left_right_elbow_frontal_mirror",max_elbow_x_mirror_error<=0.09,f"elbow x mirror error {max_elbow_x_mirror_error:.3f}m; expected <=0.09m"),
    ("feet_above_floor",min_toe_height>=-0.015,f"toe penetrates floor: min z {min_toe_height:.3f}m; allowed >=-0.015m"),
    ("toe_ground_approximate",max_toe_abs<=0.14,f"max abs toe-tip height {max_toe_abs:.3f}m; heuristic <=0.14m")
]
for name,passed,note in checks:
    if not passed:errors.append({"name":name,"reason":note})
report={
    "exerciseId":"pushup",
    "trainerId":"trainer_female_01",
    "source":str(Path(bpy.data.filepath).relative_to(ROOT)),
    "status":"CANDIDATE_REVIEW_REQUIRED" if IS_CANDIDATE else "REJECTED_FOR_INSTRUCTION",
    "purpose":"Rig instrumentation of prior rejected attempt (NOT a validated exercise).",
    "diagnosticThresholdsAreHeuristics":True,
    "checks":[{"name":n,"passed":p,"detail":d} for n,p,d in checks],
    "failures":errors,
    "manualReviewRequired":True,
    "frameSamples":data
}
OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("UTRO7_RIG_AUDIT",json.dumps({"failed":[x["name"] for x in errors],"checks":len(checks),
 "shoulderDropM":shoulder_drop,"maxWristErrorM":max_wrist_lock},ensure_ascii=False),flush=True)
print("UTRO7_REPORT_PATH",str(OUTPUT),flush=True)
