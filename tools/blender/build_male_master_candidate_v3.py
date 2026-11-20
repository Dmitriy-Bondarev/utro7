"""Male trainer v3 candidate. Real CC0 garment/hair meshes and native MakeHuman body.
Output to PRIVATE candidate only until browser pose review succeeds.
"""
import bpy,sys,importlib
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'assets/trainer_master/private/opengym3d_cc0/male_native_cc0.blend'
REF=ROOT/'assets/trainer_master/private/opengym3d_cc0/push_up_without_blender_weightchannel.glb'
MHCLO=ROOT/'assets/trainer_master/private/cc0_male_clothes/mhclo'
DATA=Path.home()/'Library/Application Support/Blender/5.3/extensions/.user/user_default/mpfb/data'
OUT=ROOT/'assets/trainer_master/private/opengym3d_cc0/candidates/male_v3_real_outfit_preview.glb'
bpy.ops.wm.open_mainfile(filepath=str(BASE))
body=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='Human')
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
def imp(s,k):
 for name in list(sys.modules):
  if name.endswith(s):return getattr(importlib.import_module(name),k)
 raise RuntimeError('Module missing '+s)
HS=imp('mpfb.services.humanservice','HumanService')
assets=[
 ('clothes/namuhekam_male_polo_shirt/namuhekam_male_polo_shirt.mhclo','Clothes','shirt'),
 ('clothes/cortu_jeans_shorts/cortu_jeans_shorts.mhclo','Clothes','shorts'),
 ('clothes/shoes01/shoes01.mhclo','Clothes','shoes'),
 ('hair/cortu_short_messy_hair/cortu_short_messy_hair.mhclo','Hair','hair'),
 ('eyes/low-poly/low-poly.mhclo','Eyes','eyes'),
 ('eyebrows/eyebrow001/eyebrow001.mhclo','Eyebrows','brows')
]
for filename,asset_type,short in assets:
 path=(DATA/filename) if filename.startswith(('clothes/shoes01/','eyes/','eyebrows/')) else MHCLO/filename
 if not path.is_file():raise FileNotFoundError(str(path))
 obj=HS.add_mhclo_asset(str(path),body,asset_type=asset_type,subdiv_levels=0,material_type='BLENDER',set_up_rigging=True)
 obj['trainer_asset_type']=short
 print('FITTED',short,len(obj.data.vertices),len(obj.vertex_groups),flush=True)
# Bake only MakeHuman masks at rest; preserve rigging after applying.
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True);bpy.context.view_layer.objects.active=body
for modifier in list(body.modifiers):
 if modifier.type=='ARMATURE':modifier.show_viewport=False
if body.data.shape_keys:
 bpy.ops.object.shape_key_remove(all=True,apply_mix=True)
for modifier in list(body.modifiers):
 if modifier.type=='MASK':
  modifier.show_viewport=True;modifier.show_render=True
  bpy.ops.object.modifier_apply(modifier=modifier.name)
  print('HIDE_BODY_UNDER_GARMENTS',len(body.data.vertices),flush=True)
for modifier in list(body.modifiers):
 if modifier.type=='ARMATURE':modifier.show_viewport=True
def mat(name,color,rough=.78):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=rough
 return m
pallet={
 'skin':mat('natural skin — warm medium',(.64,.47,.37),.93),
 'shirt':mat('navy fitted performance tee',(.022,.13,.36),.82),
 'shorts':mat('dark graphite athletic shorts',(.062,.074,.087),.9),
 'shoes':mat('dark sport sneakers',(.086,.11,.15),.73),
 'hair':mat('short natural brown hair',(.105,.069,.046),.9),
 'eyes':mat('natural eye whites',(.89,.87,.83),.45),
 'brows':mat('natural dark eyebrows',(.085,.063,.047),.89)
}
for obj in bpy.data.objects:
 if obj.type!='MESH':continue
 kind='skin' if obj==body else obj.get('trainer_asset_type','skin')
 material=pallet[kind]
 obj.data.materials.clear();obj.data.materials.append(material)
 for face in obj.data.polygons:face.material_index=0;face.use_smooth=True
# Copy bone LOCAL (rest-relative) transforms. Do not reapply source world matrices.
bpy.ops.import_scene.gltf(filepath=str(REF))
source=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o!=rig)
assert set(source.pose.bones.keys())==set(rig.pose.bones.keys())
rig.animation_data_clear()
for target_bone in rig.pose.bones:
 target_bone.rotation_mode='QUATERNION'
for frame in range(1,38):
 bpy.context.scene.frame_set(frame)
 # local transforms in same 163-bone MakeHuman topology, despite differing rest proportions
 for pb in rig.pose.bones:
  sp=source.pose.bones[pb.name]
  pb.matrix_basis=sp.matrix_basis.copy()
 bpy.context.view_layer.update()
 for pb in rig.pose.bones:
  pb.keyframe_insert(data_path='location',frame=frame)
  pb.keyframe_insert(data_path='rotation_quaternion',frame=frame)
  pb.keyframe_insert(data_path='scale',frame=frame)
 if frame in [1,10,20,30]:
  head=rig.matrix_world@rig.pose.bones['head'].matrix
  root=rig.matrix_world@rig.pose.bones['root'].matrix
  foot=rig.matrix_world@rig.pose.bones['foot.L'].matrix
  print('POSE',frame,'head',tuple(round(x,3) for x in head.translation),'foot',tuple(round(x,3) for x in foot.translation),'root',tuple(round(x,3) for x in root.translation),flush=True)
# Remove imported reference after keyframes recorded on new male.
for obj in list(bpy.data.objects):
 if obj.type=='ARMATURE' and obj!=rig:bpy.data.objects.remove(obj,do_unlink=True)
 elif obj.type=='MESH' and obj!=body and not obj.get('trainer_asset_type'):bpy.data.objects.remove(obj,do_unlink=True)
for action in list(bpy.data.actions):
 if action!=rig.animation_data.action:bpy.data.actions.remove(action,do_unlink=True)
bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=37;bpy.context.scene.render.fps=24
bpy.context.scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
 if obj==rig or obj.type=='MESH':obj.select_set(True)
bpy.context.view_layer.objects.active=rig
OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True,export_animations=True,export_frame_range=True,export_materials='EXPORT',export_yup=True)
print('OUTPUT',str(OUT),OUT.stat().st_size,flush=True)
