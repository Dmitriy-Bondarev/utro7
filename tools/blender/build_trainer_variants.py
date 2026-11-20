"""Create rigged CC0 trainers in sportswear for 7 утра.
Source: OpenGym3D / MakeHuman MPFB (CC0), animation via OpenGym3D CC0.
Input reference GLBs retained privately; no Human Generator trial content.
Output clips and appearance require user visual review and technique assessment.
"""
import bpy, sys, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sex=next((x.split('=',1)[1] for x in sys.argv if x.startswith('--sex=')),'male')
move=next((x.split('=',1)[1] for x in sys.argv if x.startswith('--move=')),'pushup')
assert sex in ('male','female') and move in ('pushup','squat')
PRIVATE=ROOT/'assets/trainer_master/private/opengym3d_cc0'
ref=PRIVATE/('push_up_without_blender_weightchannel.glb' if move=='pushup' else 'squat_without_blender_weightchannel.glb')
out=ROOT/'preview/rotatable-cc0-trainer'/f'trainer_{sex}_{move}.glb'
if sex=='female':
    fem=PRIVATE/'female_default_cc0.blend'
    if not fem.exists():
        print('FEMALE_SOURCE_MISSING',fem,flush=True);raise FileNotFoundError(fem)
    bpy.ops.wm.open_mainfile(filepath=str(fem))
    target_rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='Human')
    bpy.ops.import_scene.gltf(filepath=str(ref))
    ref_rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o!=target_rig)
    assert len(target_rig.data.bones)==len(ref_rig.data.bones)==163
    # Retarget bone world-space pose against each character's OWN rest skeleton.
    # Sharing source local FCurves made the different female proportions remain upright.
    target_rig.animation_data_clear()
    for pb in target_rig.pose.bones: pb.rotation_mode='QUATERNION'
    ordered=sorted(target_rig.pose.bones,key=lambda pb: len(pb.parent_recursive))
    for frame in range(1,38):
        bpy.context.scene.frame_set(frame)
        source_pose={name:pb.matrix.copy() for name,pb in ref_rig.pose.bones.items()}
        for pb in ordered:
            name=pb.name
            male_rest=ref_rig.data.bones[name].matrix_local
            female_rest=target_rig.data.bones[name].matrix_local
            pb.matrix=female_rest @ male_rest.inverted() @ source_pose[name]
        bpy.context.view_layer.update()
        for pb in ordered:
            pb.keyframe_insert(data_path='location',frame=frame)
            pb.keyframe_insert(data_path='rotation_quaternion',frame=frame)
            pb.keyframe_insert(data_path='scale',frame=frame)
    bpy.context.scene.frame_set(1)
    print('FEMALE_RETARGET_BAKED',move,flush=True)
    for old in list(bpy.data.actions):
        if old != target_rig.animation_data.action:
            bpy.data.actions.remove(old,do_unlink=True)
    for o in list(bpy.data.objects):
        if o not in (target_rig,mesh):bpy.data.objects.remove(o,do_unlink=True)
    # Female CC0 MPFB native mesh uses built-in geometry helper mask.
    for mod in list(mesh.modifiers):
        if mod.type=='MASK':mod.show_render=True
else:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ref))
    mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='Human')
    target_rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    for o in list(bpy.data.objects):
        if o not in (target_rig,mesh):bpy.data.objects.remove(o,do_unlink=True)
assert all(b in target_rig.data.bones for b in ['head','eye.L','eye.R','foot.L','foot.R'])
# Fabric look is a material mask over skinned geometry, not separate simulated cloth.
def material(name,rgb,roughness=.8):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*rgb,1);mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*rgb,1)
    bsdf.inputs['Roughness'].default_value=roughness
    return mat
skin=material('Skin tone / face',(.73,.59,.50) if sex=='female' else (.67,.54,.46))
shirt=material('Performance sports top',(.07,.39,.43) if sex=='female' else (.018,.11,.42))
shorts=material('Charcoal sports shorts',(.049,.054,.073))
shoes=material('Charcoal training footwear',(.10,.12,.15))
soles=material('Light sole',(.72,.75,.78))
hairmat=material('Chocolate hair',(.13,.065,.042) if sex=='female' else (.095,.063,.046),.95)
eyewhite=material('Eye sclera',(.94,.91,.85),.43)
iris=material('Brown iris',(.17,.10,.065),.36)
pupil=material('Dark pupil',(.021,.021,.022),.3)
brow=material('Eyebrows',(.13,.073,.056),.96)
mesh.data.materials.clear()
for m in [skin,shirt,shorts,shoes,soles]:mesh.data.materials.append(m)
zs=(.87,1.32,.71,.99,1.19,.34,.37) if sex=='female' else (1.005,1.465,.75,1.055,1.28,.39,.435)
toplow,tophigh,shortlow,shorthigh,sleevez,torsoX,sleeveX=zs
from collections import Counter
stats=Counter()
for face in mesh.data.polygons:
    v=[mesh.data.vertices[i].co for i in face.vertices]
    x=sum(k.x for k in v)/len(v);z=sum(k.z for k in v)/len(v)
    idx=0
    if z < .032 and abs(x)>.065:idx=4
    elif z<.19 and abs(x)>.065:idx=3
    elif shortlow<=z<shorthigh and abs(x)<torsoX:idx=2
    elif toplow<=z<=tophigh:
        if abs(x)<torsoX or (z>sleevez and abs(x)<sleeveX):idx=1
    face.material_index=idx;face.use_smooth=True;stats[idx]+=1
print('CLOTHING',sex,move,stats,flush=True)
# New accessories are bound to the existing head joint (not a static PNG).
def accessory(name,points,faces,mat,bone='head'):
    data=bpy.data.meshes.new(name)
    data.from_pydata(points,[],faces);data.update()
    o=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    group=o.vertex_groups.new(name=bone);group.add(list(range(len(points))),1.0,'REPLACE')
    mod=o.modifiers.new('Head-follow-rig','ARMATURE');mod.object=target_rig
    for p in o.data.polygons:p.use_smooth=True
    return o
def ellipsoid(name,center,radii,mat,bone='head',theta_max=math.pi,segments=24,rings=12):
    verts=[];faces=[]
    for i in range(rings+1):
        t=theta_max*i/rings
        for j in range(segments):
            phi=2*math.pi*j/segments
            verts.append((center[0]+radii[0]*math.sin(t)*math.cos(phi),
                          center[1]+radii[1]*math.sin(t)*math.sin(phi),
                          center[2]+radii[2]*math.cos(t)))
    for i in range(rings):
        for j in range(segments):
            k=i*segments+j;n=(j+1)%segments
            faces.append((k,i*segments+n,(i+1)*segments+n,(i+1)*segments+j))
    return accessory(name,verts,faces,mat,bone)
head=target_rig.data.bones['head']
headbase=head.head_local
headtop=1.665 if sex=='female' else 1.715
center=(0,-.045,headtop-.093)
ellipsoid('Short textured hair / scalp' if sex=='male' else 'Long chestnut hair / scalp',
          center,(.093,.107,.103),hairmat,theta_max=1.32,segments=28,rings=9)
if sex=='female':
    # Ponytail to make the trainer immediately distinguishable in 3D.
    ellipsoid('Ponytail / tied hair',(.0,.080,headtop-.135),(.052,.065,.112),hairmat,theta_max=math.pi,segments=18,rings=10)
    ellipsoid('Hair tie',(.0,.105,headtop-.075),(.038,.036,.028),brow,theta_max=math.pi,segments=16,rings=8)
for side in ('L','R'):
    b=target_rig.data.bones['eye.'+side]
    tip=b.tail_local
    # Eye bones define the actual face anchor; offset toward the front (-Y).
    x=tip.x;y=tip.y-.008;z=tip.z
    ellipsoid(side+' sclera',(x,y,z),(.022,.013,.018),eyewhite,segments=16,rings=10)
    ellipsoid(side+' iris',(x,y-.011,z),(.011,.006,.011),iris,segments=16,rings=8)
    ellipsoid(side+' pupil',(x,y-.017,z),(.005,.004,.006),pupil,segments=12,rings=7)
    ellipsoid(side+' eyebrow',(x,y+.006,z+.029),(.023,.006,.0055),brow,segments=12,rings=6)
# Keep both armature & skinned meshes, exclude floor/probes from GLB.
bpy.context.scene.frame_start=1
bpy.context.scene.frame_end=37
bpy.context.scene.render.fps=24
bpy.context.scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
target_rig.select_set(True);bpy.context.view_layer.objects.active=target_rig
for obj in bpy.data.objects:
    if obj.type=='MESH':obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_animations=True,
    export_frame_range=True,export_materials='EXPORT',export_yup=True)
print('READY',str(out),out.stat().st_size,flush=True)
