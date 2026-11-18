"""Install official Human Generator trial addon into Blender's local user profile.

Input must be downloaded from https://downloads.humangenerator3d.com/
Private trial files are not committed. This runs user Blender preferences,
does not install demo assets or create an accepted trainer by itself.

Run: blender -b -t 4 -P tools/blender/trainer_master/install_humgen_trial.py
"""
import bpy
from pathlib import Path
import traceback
ROOT=Path(__file__).resolve().parents[3]
ZIP=ROOT/"assets/trainer_master/private/humgen_trial/HumGen3D_v4_0_29.zip"
assert ZIP.is_file() and ZIP.stat().st_size>5_000_000, "Official addon ZIP missing/incomplete"
print("TRIAL_SETUP_BLENDER",bpy.app.version_string,flush=True)
print("TRIAL_SETUP_ARCHIVE_BYTES",ZIP.stat().st_size,flush=True)
try:
    result=bpy.ops.preferences.addon_install(filepath=str(ZIP),overwrite=True)
    print("TRIAL_ADDON_INSTALL_OPERATOR",result,flush=True)
    result=bpy.ops.preferences.addon_enable(module="HumGen3D")
    print("TRIAL_ADDON_ENABLE_OPERATOR",result,flush=True)
    mod=bpy.context.preferences.addons.get("HumGen3D")
    assert mod is not None,"Addon not enabled"
    prefs=mod.preferences
    print("TRIAL_ADDON_PREFS_TYPE",type(prefs).__name__,flush=True)
    for prop in prefs.bl_rna.properties:
        k=prop.identifier
        if k not in {"rna_type","bl_idname"} and ("path" in k.lower() or "folder" in k.lower() or "content" in k.lower()):
            try:v=getattr(prefs,k);print("TRIAL_PREF_FIELD",k,str(v)[:180],flush=True)
            except Exception:pass
    bpy.ops.wm.save_userpref()
    print("TRIAL_ADDON_INSTALLED_AND_ENABLED",flush=True)
except Exception:
    traceback.print_exc()
    raise
