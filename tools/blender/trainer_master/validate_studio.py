"""Validate T0 studio scaffold with Blender; never imply a trainer is accepted.

Usage:
  blender -b assets/trainer_master/scenes/utro7_studio_template.blend \
    -P tools/blender/trainer_master/validate_studio.py
"""
import bpy
from pathlib import Path

scene = bpy.context.scene
expected = {
    "RV_01_FRONT_FULL",
    "RV_02_SIDE_FULL",
    "RV_03_THREE_QUARTER_FULL",
    "RV_04_FACE_CLOSEUP",
    "RV_05_HANDS_CLOSEUP",
    "RV_06_FEET_SHOES_CLOSEUP",
    "RV_07_TORSO_CLOTHING",
}
actual = {o.name for o in bpy.data.objects if o.type == "CAMERA"}
assert expected == actual, (expected - actual, actual - expected)
assert len([o for o in bpy.data.objects if o.type == "LIGHT"]) == 3
assert len([o for o in bpy.data.objects if o.type == "ARMATURE"]) == 0
assert len([o for o in bpy.data.objects if o.type == "MESH"]) == 1
assert bpy.data.objects.get("Neutral Matte Floor / Z=0") is not None
assert scene.get("utro7_asset_id") == "trainer_female_master_01"
assert scene.get("production_stage") == "T0_STUDIO_TEMPLATE"
assert scene.get("human_model_loaded") is False
assert scene.get("visual_accepted") is False
assert scene.get("source_asset_license_checked") is False
assert scene.unit_settings.system == "METRIC"
assert scene.render.resolution_y == 1800
assert scene.render.resolution_x == 1200
print("T0_STUDIO_VALIDATION_PASS", "7 cameras, 3 lights, only floor mesh, no human")
print("T0_NO_HUMAN_MODEL", "T1 blocked until licensed realistic source is imported")
