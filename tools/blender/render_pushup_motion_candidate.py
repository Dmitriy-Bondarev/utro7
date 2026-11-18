import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"assets/motion/quality-g2"
bpy.ops.wm.open_mainfile(filepath=str(OUT/"trainer-female-pushup-motion-candidate.blend"))
scene=bpy.context.scene
scene.render.resolution_x=960
scene.render.resolution_y=600
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.fps=30
frames=OUT/"_frames"
frames.mkdir(exist_ok=True)
scene.render.filepath=str(frames/"pushup_")
scene.camera=bpy.data.objects["G1 Pose Review A_side"]
print("G2_RENDER_START",scene.frame_start,scene.frame_end,flush=True)
bpy.ops.render.render(animation=True)
print("G2_RENDER_DONE",flush=True)
