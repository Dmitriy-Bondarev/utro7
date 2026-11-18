"""Frame-by-frame diagnostic audit of EX-04 squat candidate, NOT fitness approval."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
rig=next(o for o in bpy.data.objects if o.type=="ARMATURE")
samples=[]
for frame in range(scene.frame_start,scene.frame_end+1):
    scene.frame_set(frame);bpy.context.view_layer.update()
    obj=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
    row={"frame":frame,"legs":{}}
    for side in ("l","r"):
        thigh=obj.pose.bones["thigh_"+side]
        calf=obj.pose.bones["calf_"+side]
        ball=obj.pose.bones["ball_"+side]
        hip=obj.matrix_world@thigh.head
        knee=obj.matrix_world@thigh.tail
        ankle=obj.matrix_world@calf.tail
        toe=obj.matrix_world@ball.tail
        goal=bpy.data.objects["SquatAnkleLock_"+side].location
        angle=math.degrees((hip-knee).angle(ankle-knee))
        row["legs"][side]={
          "hip":[round(float(v),5) for v in hip],
          "knee":[round(float(v),5) for v in knee],
          "ankle":[round(float(v),5) for v in ankle],
          "toe":[round(float(v),5) for v in toe],
          "kneeAngleDeg":round(angle,2),
          "ankleTargetErrorM":round((ankle-goal).length,5)
        }
    samples.append(row)
top=samples[0];bottom=samples[50]
checks={
 "120_frames":len(samples)==120,
 "ankles_fixed":max(s["legs"][d]["ankleTargetErrorM"] for s in samples for d in ("l","r"))<.01,
 "knee_angle_symmetric":max(abs(s["legs"]["l"]["kneeAngleDeg"]-s["legs"]["r"]["kneeAngleDeg"]) for s in samples)<5,
 "top_knees_nearly_extended":min(top["legs"][s]["kneeAngleDeg"] for s in ("l","r"))>165,
 "bottom_knees_bent":max(bottom["legs"][s]["kneeAngleDeg"] for s in ("l","r"))<125,
 "knee_bend_facing_forward":min((s["legs"][side]["knee"][1]-s["legs"][side]["ankle"][1]) for s in samples[34:86] for side in ("l","r"))<-.025,
 "toe_placement_doesnt_drift":max(abs(s["legs"][side]["toe"][1]-samples[0]["legs"][side]["toe"][1]) for s in samples for side in ("l","r"))<.04,
 "toe_above_floor":min(s["legs"][side]["toe"][2] for s in samples for side in ("l","r"))>-.01,
 "loop_closure":max(math.dist(samples[0]["legs"][side][joint],samples[-1]["legs"][side][joint]) for side in ("l","r") for joint in ("hip","knee","ankle","toe"))<.01
}
rep={"exercise":"squat","trainer":"trainer_female_01","status":"REVIEW","checks":checks,
 "failed":[k for k,v in checks.items() if not v],
 "top":top,"bottom":bottom,
 "metrics":{
   "kneeAnglesTop":[top["legs"][s]["kneeAngleDeg"] for s in ("l","r")],
   "kneeAnglesBottom":[bottom["legs"][s]["kneeAngleDeg"] for s in ("l","r")],
   "maxToeYDriftM":round(max(abs(s["legs"][side]["toe"][1]-samples[0]["legs"][side]["toe"][1]) for s in samples for side in ("l","r")),4),
   "minToeHeightM":round(min(s["legs"][side]["toe"][2] for s in samples for side in ("l","r")),4),
   "maxAnkleErrorM":round(max(s["legs"][side]["ankleTargetErrorM"] for s in samples for side in ("l","r")),4)
 },
 "note":"Geometry heuristics only; exercise technique is NOT professionally approved"}
out=R/"docs/implementation/squat_g1_geometry_audit.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+"\n")
print("SQUAT_AUDIT",json.dumps({"checks":checks,"metrics":rep["metrics"]},ensure_ascii=False),flush=True)
