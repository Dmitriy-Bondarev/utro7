"""Functional trial probe ONLY (licensed trial's single male preset).

Tests Blender 5.3 compatibility, 3D mesh materials and rig completeness.
NEVER uses this male trial as a female master trainer or publishes a trial asset.
"""
import bpy
from pathlib import Path
from HumGen3D import Human
from HumGen3D.backend.preferences.preference_func import get_prefs

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"assets/trainer_master/private/humgen_trial"
p=get_prefs()
assert p.is_trial
print("HUMGEN_TRIAL_API_READY",bpy.app.version_string,p.is_trial,flush=True)
preset="models/male/Caucasian Presets/Caucasian 1.jpg"
assert (Path(p.filepath)/preset.replace(".jpg",".json")).is_file()
# Existing default cube / light / camera are not needed.
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob,do_unlink=True)
print("HUMGEN_START_PRESET",preset,flush=True)
human=Human.from_preset(preset)
print("HUMGEN_CREATED",human.name,"GENDER",human.gender,flush=True)
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
rigs=[o for o in bpy.data.objects if o.type=="ARMATURE"]
print("HUMGEN_MESHES",[(o.name,len(o.data.vertices),len(o.material_slots)) for o in meshes][:20],flush=True)
print("HUMGEN_RIGS",[(o.name,len(o.data.bones)) for o in rigs][:15],flush=True)
print("HUMGEN_HAIR",[(o.name,o.type) for o in bpy.data.objects if "hair" in o.name.lower()][:10],flush=True)
assert meshes and rigs
assert len(rigs[0].data.bones)>30, "Rig too simple even for technical check"
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"humgen_male_trial_technical_probe.blend"))
print("HUMGEN_TRIAL_TECHNICAL_PROBE_SAVED",flush=True)
