"""Install the OFFICIAL Human Generator trial content pack for Blender.

Uses vendor's own Blender operator. The downloaded .hgpack is validated
beforehand and stays ignored under assets/trainer_master/private/.
Does not unlock paid presets or create a female trainer.

Run: blender -b -t 4 -P tools/blender/trainer_master/install_humgen_content.py
"""
import bpy
import zipfile
from pathlib import Path
from HumGen3D.backend.preferences.preference_func import get_prefs

ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/"assets/trainer_master/private/humgen_trial/HG_Trial_Content.hgpack"
FOLDER=ROOT/"assets/trainer_master/private/humgen_trial/content"
assert PACK.is_file() and PACK.stat().st_size>250_000_000,"Trial content pack missing or incomplete"
with zipfile.ZipFile(PACK) as z:
    bad=[i.filename for i in z.infolist() if i.filename.startswith("/") or ".." in Path(i.filename).parts]
    assert not bad, "Unexpected paths in vendor package"
    assert "content_packs/Trial_Content.json" in z.namelist()
FOLDER.mkdir(parents=True,exist_ok=True)

pref=get_prefs()
pref.filepath=str(FOLDER)+"/"
print("HG_TRIAL_CONTENT_FOLDER",pref.filepath,flush=True)
coll=bpy.context.scene.installpacks_col
coll.clear()
item=coll.add()
item.name=str(PACK)
item.pack_name=str(PACK)
item.json_path="content_packs/Trial_Content.json"
item.alert="None"
print("HG_TRIAL_CONTENT_INSTALL_START",flush=True)
res=bpy.ops.hg3d.cpackinstall()
print("HG_TRIAL_CONTENT_INSTALL_OPERATOR",res,flush=True)
assert (FOLDER/"content_packs/Trial_Content.json").is_file(), "Trial manifest missing after vendor install"
print("HG_TRIAL_CONTENT_FILE_COUNT",sum(1 for p in FOLDER.rglob("*") if p.is_file()),flush=True)
print("HG_TRIAL_IS_TRIAL",pref.is_trial,flush=True)
assert pref.is_trial, "Vendor should detect trial content"
bpy.ops.wm.save_userpref()
print("HG_TRIAL_CONTENT_INSTALLED",flush=True)
