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
OUT=ROOT/'assets/trainer_master/private/opengym3d_cc0/candidates/male_v6_textured_hair_preview.glb'
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
# Apply garment smoothing on REST geometry and make clothing follow the skin's armature weights.
# This avoids seams torn apart when the push-up rig bends the shoulder.
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils import geometry
from collections import defaultdict
body.update_from_editmode()
tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get(),epsilon=0.0)
def project_body_weights(garment):
  vertex_groups=garment.vertex_groups
  names=[g.name for g in body.vertex_groups]
  for g in list(vertex_groups):vertex_groups.remove(g)
  for name in names:vertex_groups.new(name=name)
  vg_indexes=[g.index for g in body.vertex_groups]
  old_verts=body.data.vertices
  weights=[{vg.group:vg.weight for vg in v.groups} for v in old_verts]
  poly_list=body.data.polygons
  modified=0
  for vert in garment.data.vertices:
    co,normal,pidx,dist=tree.find_nearest(vert.co)
    if pidx is None:continue
    # nearest body face, normalized arithmetic blending of influences
    vertices=[old_verts[i] for i in poly_list[pidx].vertices]
    values=defaultdict(float)
    scale=sum(1/((v.co-co).length_squared+.00001) for v in vertices)
    for source in vertices:
      weight=1/((source.co-co).length_squared+.00001)/scale
      for grp,w in weights[source.index].items():values[grp]+=weight*w
    tot=sum(values.values()) or 1.0
    for idx,w in values.items():
      if w>0.003:
        garment.vertex_groups[idx].add([vert.index],w/tot,'REPLACE')
    modified+=1
  print('WEIGHTS_TRANSFERRED',garment.name,modified,flush=True)
def clean_mesh(obj,kind):
  if kind in ('shirt','shorts'):
    # Preserve real garment geometry but make it less prone to clipping into body.
    # Clothing now uses nearest-body skinning rather than the rough proxy weights.
    project_body_weights(obj)
    for v in obj.data.vertices:v.co+=v.normal*(0.020 if kind=='shirt' else 0.011)
    sub=obj.modifiers.new('Smoothed actual CC0 garment','SUBSURF')
    sub.subdivision_type='CATMULL_CLARK';sub.levels=1;sub.render_levels=1
    solid=obj.modifiers.new('Fabric edge thickness','SOLIDIFY')
    solid.thickness=0.005;solid.offset=0.15
  elif kind=='hair':
    sub=obj.modifiers.new('Smoothed hair cap','SUBSURF')
    sub.subdivision_type='CATMULL_CLARK';sub.levels=2;sub.render_levels=2
  elif kind=='shoes':
    sub=obj.modifiers.new('Rounded shoe geometry','SUBSURF')
    sub.levels=1;sub.render_levels=1
for obj in list(bpy.data.objects):
 if obj.type=='MESH' and obj!=body: clean_mesh(obj,obj.get('trainer_asset_type','skin'))
# Bake subdivision and fabric thickness into the GLB geometry at rest;
# glTF export does not reliably export unapplied Blender modifier stacks.
for obj in list(bpy.data.objects):
 if obj.type!='MESH' or obj==body:continue
 bpy.ops.object.select_all(action='DESELECT')
 obj.select_set(True);bpy.context.view_layer.objects.active=obj
 for m in obj.modifiers:
  if m.type=='ARMATURE':m.show_viewport=False
 for m in list(obj.modifiers):
  if m.type in {'SUBSURF','SOLIDIFY'}:
   bpy.ops.object.modifier_apply(modifier=m.name)
 for m in obj.modifiers:
  if m.type=='ARMATURE':m.show_viewport=True
 print('BAKED_GARMENT',obj.name,'vertices',len(obj.data.vertices),'faces',len(obj.data.polygons),flush=True)
# Male CC0 UV skin texture corrects the flat plastic-looking face.
skin_image=bpy.data.images.load(str(ROOT/'assets/trainer_master/private/cc0_male_clothes/skin_balanced_male_cc0.png'),check_existing=True)
skin_image.pack()
skin_image.colorspace_settings.name='sRGB'
body_skin=pallet['skin'];nts=body_skin.node_tree.nodes
tex=nts.new('ShaderNodeTexImage');tex.image=skin_image;tex.interpolation='Linear'
body_skin.node_tree.links.new(tex.outputs['Color'],nts.get('Principled BSDF').inputs['Base Color'])
# Short-haired CC0 photographic strand texture with alpha and normal map.
hair_mat=pallet['hair'];hn=hair_mat.node_tree.nodes
hair_photo=bpy.data.images.load(str(ROOT/'assets/trainer_master/private/cc0_male_clothes/hair_brown_tinted_cc0.png'),check_existing=True)
hair_photo.pack();hair_photo.colorspace_settings.name='sRGB'
hair_tex=hn.new('ShaderNodeTexImage');hair_tex.image=hair_photo;hair_tex.interpolation='Linear'
hair_bsdf=hn.get('Principled BSDF')
hair_mat.node_tree.links.new(hair_tex.outputs['Color'],hair_bsdf.inputs['Base Color'])
hair_mat.node_tree.links.new(hair_tex.outputs['Alpha'],hair_bsdf.inputs['Alpha'])
try:hair_mat.surface_render_method='DITHERED'
except Exception:pass
hair_norm_img=bpy.data.images.load(str(ROOT/'assets/trainer_master/private/cc0_male_clothes/short_messy_objnorm.png'),check_existing=True)
hair_norm_img.pack();hair_norm_img.colorspace_settings.name='Non-Color'
hair_norm=hn.new('ShaderNodeTexImage');hair_norm.image=hair_norm_img
normal=hn.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.3
hair_mat.node_tree.links.new(hair_norm.outputs['Color'],normal.inputs['Color'])
hair_mat.node_tree.links.new(normal.outputs['Normal'],hair_bsdf.inputs['Normal'])

# Small iris and pupil discs follow the head bone; no oversized eye spheres.
def iris_disc(name,x,y,z,radius,material):
  segments=20
  from math import sin,cos,pi
  coords=[(x,y,z)]+[(x+radius*cos(2*pi*i/segments),y,z+radius*sin(2*pi*i/segments)) for i in range(segments)]
  faces=[(0,i+1,(i+1)%segments+1) for i in range(segments)]
  m=bpy.data.meshes.new(name);m.from_pydata(coords,[],faces);m.update()
  o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o)
  o.data.materials.append(material);o['trainer_asset_type']='iris'
  group=o.vertex_groups.new(name='head');group.add(list(range(len(coords))),1.0,'REPLACE')
  arm=o.modifiers.new('Follow head rig','ARMATURE');arm.object=rig
  return o
iris_mat=mat('brown natural iris',(.16,.083,.047),.38)
pupil_mat=mat('dark round pupil',(.018,.014,.014),.28)
for x in [-.0294,.0294]:
 iris_disc('iris',x,-.1437,1.6195,.0085,iris_mat)
 iris_disc('pupil',x,-.1444,1.6195,.0038,pupil_mat)
for obj in bpy.data.objects:
 if obj.type!='MESH':continue
 kind='skin' if obj==body else obj.get('trainer_asset_type','skin')
 material=pallet.get(kind)
 if material is None:continue
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
