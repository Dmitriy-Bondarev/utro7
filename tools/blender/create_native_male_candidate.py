import bpy,sys,importlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def imp(s,k):
 for n in sys.modules:
  if n.endswith(s):return getattr(importlib.import_module(n),k)
 raise RuntimeError(s)
HS=imp('mpfb.services.humanservice','HumanService')
HOP=imp('mpfb.entities.objectproperties','HumanObjectProperties')
TS=imp('mpfb.services.targetservice','TargetService')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
base=HS.create_human()
for k,val in [('gender',1.0),('muscle',.46),('weight',.46),('proportions',.82)]:
 HOP.set_value(k,val,entity_reference=base)
TS.reapply_macro_details(base)
rig=HS.add_builtin_rig(base,'default')
print('MALE_NATIVE',base.name,len(base.data.vertices),len(rig.data.bones),tuple(round(v,2) for v in base.dimensions),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/trainer_master/private/opengym3d_cc0/male_native_cc0.blend'))
