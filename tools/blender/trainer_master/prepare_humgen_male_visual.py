"""T0/T1 visual candidate: authorized Human Generator trial male only.

License: private technical evaluation, NOT commercial distribution.
Use vendor-provided unlocked presets; never unlock trial-only assets.
"""
import bpy
from pathlib import Path
from HumGen3D import Human
from HumGen3D.backend.preferences.preference_func import get_prefs
ROOT=Path(__file__).resolve().parents[3]
TRIAL=ROOT/"assets/trainer_master/private/humgen_trial"
SOURCE=TRIAL/"humgen_male_trial_technical_probe.blend"
TARGET=TRIAL/"humgen_male_trial_visual_candidate.blend"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
rig=next(o for o in bpy.data.objects if o.type=="ARMATURE")
h=Human.from_existing(rig)
prefs=get_prefs()
assert prefs.is_trial and h.gender=="male"
print("MALE_TRIAL_SOURCE",h.name,len(rig.data.bones),flush=True)
hair="hair/head/male/Short/Short Side Part.json"
outfit="outfits/male/Extra Outfits Pack/Relaxed Fit.blend"
for kind,name,action in [
 ("hair",hair,lambda:h.hair.regular_hair.set(name)),
 ("outfit",outfit,lambda:h.clothing.outfit.set(name))]:
 try:
  assert (Path(prefs.filepath)/name).is_file()
  action()
  print("TRIAL_APPLIED",kind,name,flush=True)
 except Exception as e:
  print("TRIAL_PROVISIONAL_APPEARANCE_ERROR",kind,type(e).__name__,str(e)[:400],flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET))
print("TRIAL_MALE_VISUAL_CANDIDATE_SAVED",str(TARGET),flush=True)
print("TRIAL_SCENE_OBJECTS",[(o.name,o.type) for o in bpy.data.objects][:22],flush=True)
