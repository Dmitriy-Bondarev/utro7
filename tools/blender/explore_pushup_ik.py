"""Search rig root height and IK elbow pole angles for a symmetric push-up starting pose.

This is a geometric baseline optimizer, NOT a fitness-technique approval.
Launch with the original rejected .blend:
blender -b assets/motion/quality-v2/trainer-female-pushup.blend -P tools/blender/explore_pushup_ik.py
"""
import bpy
import math
import json
from mathutils import Vector
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
rig=next(o for o in bpy.data.objects if o.type=="ARMATURE")
scene=bpy.context.scene
ik={side:next(c for c in rig.pose.bones["lowerarm_"+side].constraints if c.type=="IK") for side in ("l","r")}


def collect(frame):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    actual=rig.evaluated_get(dg)
    result={}
    for side in ("l","r"):
        upper=actual.pose.bones["upperarm_"+side]
        lower=actual.pose.bones["lowerarm_"+side]
        shoulder=actual.matrix_world@upper.head
        elbow=actual.matrix_world@upper.tail
        wrist=actual.matrix_world@lower.tail
        target=bpy.data.objects["WristLock_"+side].location
        toe=actual.matrix_world@actual.pose.bones["ball_"+side].tail
        result[side]={
            "angle":round(math.degrees((shoulder-elbow).angle(wrist-elbow)),1),
            "S":[round(x,3) for x in shoulder],
            "E":[round(x,3) for x in elbow],
            "W":[round(x,3) for x in wrist],
            "error":round((wrist-target).length,4),
            "toeZ":round(toe.z,3)
        }
    return result


results=[]
for z in (0.18,0.19,0.20,0.205,0.21,0.215,0.22,0.23):
    rig.location.z=z
    for left in (0,math.pi,-math.pi/2,math.pi/2):
        ik["l"].pole_angle=left
        for right in (0,math.pi,-math.pi/2,math.pi/2):
            ik["r"].pole_angle=right
            top=collect(1)
            low=collect(11)
            tl,tr=top["l"],top["r"]
            bl,br=low["l"],low["r"]
            dy=max(abs((row["l"]["E"][1]-row["l"]["S"][1])-(row["r"]["E"][1]-row["r"]["S"][1])) for row in (top,low))
            dx=max(abs(row["l"]["E"][0]+row["r"]["E"][0]) for row in (top,low))
            wrist=max(x["error"] for row in (top,low) for x in row.values())
            toes=max(abs(x["toeZ"]-0.02) for row in (top,low) for x in row.values())
            top_elbow=min(tl["angle"],tr["angle"])
            bottom_angles=(bl["angle"]+br["angle"])/2
            # The point is to prioritize symmetrical elbow rotation and plausible upper/lower-arm angles.
            score= (
                100*max(0,150-top_elbow)/30 +
                100*max(0,bottom_angles-105)/30 +
                100*max(0,70-bottom_angles)/30 +
                450*dy +
                450*dx +
                1000*wrist +
                150*toes
            )
            results.append({"z":z,"poleAngleLeft":round(left,5),"poleAngleRight":round(right,5),
                            "score":round(score,2),"top":top,"bottom":low,
                            "dy":round(dy,3),"dx":round(dx,3),"wrist":wrist,"toes":round(toes,3)})
result=sorted(results,key=lambda item:item["score"])
out=ROOT/"docs/implementation/pushup_ik_parameter_exploration.json"
out.parent.mkdir(exist_ok=True,parents=True)
out.write_text(json.dumps({"purpose":"Research only; poses not approved","best10":result[:10],"allCandidateCount":len(result)},ensure_ascii=False,indent=2)+"\n")
print("IK_EXPLORATION_SCORES",json.dumps([{"z":r["z"],"left":r["poleAngleLeft"],"right":r["poleAngleRight"],
 "score":r["score"],"topAngles":[r["top"]["l"]["angle"],r["top"]["r"]["angle"]],
 "bottomAngles":[r["bottom"]["l"]["angle"],r["bottom"]["r"]["angle"]],
 "dy":r["dy"],"dx":r["dx"],"toe":r["toes"],"wrist":r["wrist"]} for r in result[:6]],ensure_ascii=False),flush=True)
