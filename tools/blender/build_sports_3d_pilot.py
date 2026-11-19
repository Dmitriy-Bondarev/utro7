"""Build clothed rigged CC0 athlete. Source and motion: OpenGym3D CC0-1.0.
Visual MVP: garment material segmentation on existing skinned geometry.
Not expert-approved exercise technique. No Human Generator trial assets involved.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"assets/trainer_master/private/opengym3d_cc0/push_up_without_blender_weightchannel.glb"
OUT=ROOT/"preview/rotatable-cc0-trainer/trainer_sports_pushup.glb"
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SRC))
m=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='Human')
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
def mat(name, rgb, roughness=0.84):
    obj=bpy.data.materials.new(name);obj.diffuse_color=(*rgb,1)
    obj.use_nodes=True
    bsdf=obj.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*rgb,1)
    bsdf.inputs['Roughness'].default_value=roughness
    return obj
palette=[
 mat('01 | matte neutral skin',(.72,.74,.75)),
 mat('02 | navy blue stretch training jersey',(.014,.085,.32),.84),
 mat('03 | dark graphite athletic shorts',(.055,.065,.085),.88),
 mat('04 | charcoal training shoes',(.09,.105,.135),.69),
 mat('05 | rubber white soles',(.72,.76,.80),.75),
 mat('06 | navy sleeve trim',(.055,.09,.23),.85),
]
m.data.materials.clear()
for v in palette:m.data.materials.append(v)
from collections import Counter
counts=Counter()
def classify(vs):
    x=sum(v.co.x for v in vs)/len(vs)
    z=sum(v.co.z for v in vs)/len(vs)
    # Rest shape is standing upright in glTF and is driven by 163 skinned joints.
    # Boundaries deliberately overlap but share face edges (no clipping/z-fighting).
    if .0<=z<.025 and abs(x)>.07: return 4 # sole accents
    if z < .19 and abs(x)>.075: return 3 # shoes on feet
    if .75<=z<1.055 and abs(x)<.39: return 2 # above-knee shorts
    if 1.005 <= z <= 1.465:
        if abs(x)<=.295: return 1
        # short sleeves cover clavicle and proximal upper arms
        if z>1.28 and abs(x) < .435: return 1
    if 1.25<=z<1.405 and .43<=abs(x)<.47: return 5 # sleeve cuffs
    return 0
verts=m.data.vertices
for p in m.data.polygons:
    idx=classify([verts[i] for i in p.vertices])
    p.material_index=idx
    counts[idx]+=1
for p in m.data.polygons:
    p.use_smooth=True
print('OUTFIT FACE COUNTS',counts,flush=True)
# Avoid unrelated spatial demo objects from upstream.
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True);m.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=37;bpy.context.scene.render.fps=24
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True,
  export_animations=True,export_frame_range=True,
  export_yup=True,export_materials='EXPORT',export_image_format='AUTO')
print('EXPORTED_DRESSED_CC0',str(OUT),OUT.stat().st_size,flush=True)
# Deterministic Blender render preview at original arms-down pose from animation,
# use glTF rough rendering on authored mesh.
for o in bpy.data.objects:
    if o not in (rig,m):
        o.hide_render=True
# Make explicit studio ground as separate visualization only.
bpy.ops.mesh.primitive_plane_add(size=7,location=(0,0,-.03))
g=bpy.context.object;g.name='Render only ground';g.data.materials.append(mat('studio floor',(.64,.71,.75)))
cdata=bpy.data.cameras.new('Side 3/4');cam=bpy.data.objects.new('Side 3/4',cdata);bpy.context.scene.collection.objects.link(cam)
cam.location=(2.8,-3.0,2.0);target=Vector((0,0,.65));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cdata.type='ORTHO';cdata.ortho_scale=2.5;bpy.context.scene.camera=cam
for pos,power in [((2,-3,4),1700),((-3,1,3),1000)]:
    ld=bpy.data.lights.new('Studio area','AREA');ld.energy=power;ld.size=3.5
    lo=bpy.data.objects.new('Studio area',ld);bpy.context.scene.collection.objects.link(lo);lo.location=pos
    lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.render.engine='BLENDER_EEVEE'
bpy.context.scene.render.resolution_x=1000;bpy.context.scene.render.resolution_y=680;bpy.context.scene.render.resolution_percentage=80
bpy.context.scene.render.image_settings.file_format='PNG'
bpy.context.scene.frame_set(18)
bpy.context.scene.render.filepath='/tmp/utro7_sports_clothes_preview.png'
bpy.ops.render.render(write_still=True)
print('RENDERED_PREVIEW',flush=True)
