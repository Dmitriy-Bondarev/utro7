"""UTRO7 Trainer Master v1: neutral Blender studio template for T1 visual acceptance.

This file intentionally creates NO human: it is reusable 3D production
infrastructure, not a fake avatar or a completed master asset.

Usage:
  blender -b -t 6 -P tools/blender/trainer_master/create_studio.py

Output:
  assets/trainer_master/scenes/utro7_studio_template.blend

Never add third-party model/texture binary to the public repo without
confirmed distribution rights.
"""
import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "assets" / "trainer_master" / "scenes" / "utro7_studio_template.blend"
OUT.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "UTRO7 — Trainer Master T0 Studio"
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x = 1200
scene.render.resolution_y = 1800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False

scene.world = bpy.data.worlds.new("UTRO7 soft neutral world")
scene.world.use_nodes = True
background = scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.68, 0.72, 0.77, 1)
background.inputs["Strength"].default_value = 0.28


def collection(name):
    coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)
    return coll


character = collection("TRAINER_MASTER_IMPORT_HERE")
studio = collection("STUDIO_FLOOR")
lights = collection("LIGHTS")
cameras = collection("CAMERAS")


def move_to_collection(ob, target):
    for coll in list(ob.users_collection):
        coll.objects.unlink(ob)
    target.objects.link(ob)


# 12 m matte neutral floor. Zero plane is the contact benchmark for shoe soles.
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Neutral Matte Floor / Z=0"
move_to_collection(floor, studio)
mat = bpy.data.materials.new("Neutral studio warm gray")
mat.diffuse_color = (0.64, 0.67, 0.71, 1)
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.64, 0.67, 0.71, 1)
bsdf.inputs["Roughness"].default_value = 0.86
floor.data.materials.append(mat)


def aim(ob, point):
    target = Vector(point)
    ob.rotation_euler = (target - ob.location).to_track_quat("-Z", "Y").to_euler()


def light(name, location, energy, size, aim_point):
    bpy.ops.object.light_add(type="AREA", location=location)
    ob = bpy.context.object
    ob.name = name
    ob.data.energy = energy
    ob.data.shape = "DISK"
    ob.data.size = size
    aim(ob, aim_point)
    move_to_collection(ob, lights)


light("Key / large softbox", (-3.2, -3.4, 4.5), 650, 3.5, (0, 0, 1.05))
light("Fill / front opposite", (3.0, -2.0, 3.0), 330, 3.4, (0, 0, 1.0))
light("Rim / shape separation", (0.3, 3.0, 4.2), 500, 2.8, (0, 0, 1.0))


# 7 mandatory reproducible T1 views.
# Place the future model approximately on floor Z=0 with body center at X=Y=0.
# These are INITIAL camera targets for ~1.7m height; calibrate after import.
SHOT_SPEC = [
    ("RV_01_FRONT_FULL", (0, -6.3, 1.27), (0, 0, 0.92), 2.22),
    ("RV_02_SIDE_FULL", (6.3, 0, 1.27), (0, 0, 0.92), 2.22),
    ("RV_03_THREE_QUARTER_FULL", (4.5, -4.5, 1.32), (0, 0, 0.92), 2.30),
    ("RV_04_FACE_CLOSEUP", (0, -2.4, 1.68), (0, 0, 1.61), 0.46),
    ("RV_05_HANDS_CLOSEUP", (0, -2.3, 1.0), (0, 0, 0.99), 0.82),
    ("RV_06_FEET_SHOES_CLOSEUP", (0, -2.0, 0.28), (0, 0, 0.16), 0.68),
    ("RV_07_TORSO_CLOTHING", (1.3, -2.7, 1.22), (0, 0, 1.13), 0.92),
]


def camera(name, location, point, scale):
    bpy.ops.object.camera_add(location=location)
    ob = bpy.context.object
    ob.name = name
    ob.data.type = "ORTHO"
    ob.data.ortho_scale = scale
    ob.data.lens = 55
    aim(ob, point)
    move_to_collection(ob, cameras)
    return ob


for name, loc, point, scale in SHOT_SPEC:
    c = camera(name, loc, point, scale)
    if name == "RV_03_THREE_QUARTER_FULL":
        scene.camera = c

scene["utro7_asset_id"] = "trainer_female_master_01"
scene["master_version"] = "v1"
scene["production_stage"] = "T0_STUDIO_TEMPLATE"
scene["human_model_loaded"] = False
scene["visual_accepted"] = False
scene["technique_accepted"] = False
scene["target_height_m"] = 1.70
scene["source_asset_license_checked"] = False
scene["notes"] = "Empty studio only. Add a licensed 3D human after T0 selection. No visual acceptance implied."

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print("UTRO7_STUDIO_CREATED", str(OUT), flush=True)
print("UTRO7_STUDIO_CAMERAS", ",".join(x[0] for x in SHOT_SPEC), flush=True)
print("UTRO7_STATUS", "T0 TEMPLATE — no trainer included", flush=True)
