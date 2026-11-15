import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"assets"/"motion"/"quality-v2"
SCENE=OUT/"trainer-female-pushup.blend"
bpy.ops.wm.open_mainfile(filepath=str(SCENE))
scene=bpy.context.scene
scene.render.resolution_x=840
scene.render.resolution_y=560
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.filepath=str(OUT/"_frames"/"pushup_")
scene.frame_start=1
scene.frame_end=40
scene.render.fps=20
(OUT/"_frames").mkdir(exist_ok=True)
print("UTRO7_PUSHUP_RENDER_START",flush=True)
bpy.ops.render.render(animation=True)
print("UTRO7_PUSHUP_RENDER_DONE",flush=True)
