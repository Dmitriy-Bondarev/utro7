import bpy,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
scene=bpy.context.scene
rows=[]
for frame in range(1,97):
 scene.frame_set(frame);bpy.context.view_layer.update()
 obj=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
 sides=[]
 for s in 'lr':
  u=obj.pose.bones['upperarm_'+s];l=obj.pose.bones['lowerarm_'+s]
  S=obj.matrix_world@u.head;E=obj.matrix_world@u.tail;W=obj.matrix_world@l.tail
  toe=obj.matrix_world@obj.pose.bones['ball_'+s].tail
  goal=bpy.data.objects['WristLock_'+s].location
  sides.append({'S':list(S),'E':list(E),'W':list(W),'T':list(toe),
    'angle':math.degrees((S-E).angle(W-E)),'error':(W-goal).length,
    'bend':(E-S).cross(W-E).x})
 rows.append(sides)
top,bottom=rows[0],rows[46]
maxerror=max(q['error'] for row in rows for q in row)
minToe=min(q['T'][2] for row in rows for q in row)
maxToeDrift=max(abs(q['T'][2]-rows[0][i]['T'][2]) for row in rows for i,q in enumerate(row))
maxAngDiff=max(abs(row[0]['angle']-row[1]['angle']) for row in rows)
maxMirrorX=max(abs(row[0]['E'][0]+row[1]['E'][0]) for row in rows)
maxMirrorY=max(abs(row[0]['E'][1]-row[1]['E'][1]) for row in rows)
drop=sum(top[i]['S'][2]-bottom[i]['S'][2] for i in (0,1))/2
seam=max(math.dist(rows[0][i][p],rows[-1][i][p]) for i in (0,1) for p in ('S','E','W','T'))
checks={'96_frames':len(rows)==96,'hands_fixed':maxerror<.01,
 'toes_above_floor':minToe>-.01,'toe_height_stable':maxToeDrift<.035,
 'elbow_angles_symmetric':maxAngDiff<4,'elbows_mirrored_x':maxMirrorX<.05,
 'elbows_symmetric_y':maxMirrorY<.05,
 'top_elbows_extended':min(q['angle'] for q in top)>150,
 'bottom_elbows_bent':max(q['angle'] for q in bottom)<105,
 'shoulders_lowered':drop>.13,'loop_seam_closed':seam<.005,
 'elbows_dont_flip':all(len({q['bend']>0 for row in rows for q in (row[i],)})==1 for i in (0,1))}
report={'status':'CANDIDATE_NOT_APPROVED','checks':checks,'failed':[k for k,v in checks.items() if not v],
 'frameCount':len(rows),'fps':scene.render.fps,
 'measurements':{'topElbows':[round(q['angle'],1) for q in top],
 'bottomElbows':[round(q['angle'],1) for q in bottom],
 'shoulderDropM':round(drop,4),'maxWristSlipM':round(maxerror,4),
 'minToeZ':round(minToe,4),'maxToeDriftM':round(maxToeDrift,4),
 'maxElbowAngleDiff':round(maxAngDiff,2),'maxMirrorX':round(maxMirrorX,4),
 'maxMirrorY':round(maxMirrorY,4),'loopSeamM':round(seam,5)},
 'warning':'Geometry heuristics only; does not certify safe exercise technique.'}
out=root/'docs/implementation/g2_pushup_motion_audit.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('G2_AUDIT',json.dumps(report,ensure_ascii=False),flush=True)
if report['failed']:raise SystemExit('G2 motion geometry failed')
