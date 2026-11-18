"""Render EX-04 candidate video, 120 frames / 30 fps / 800 x 800."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"assets"/"motion"/"squat-g1"
bpy.ops.wm.open_mainfile(filepath=str(OUT/"trainer-female-squat-candidate.blend"))
s=bpy.context.scene
s.render.resolution_x=800;s.render.resolution_y=800
s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGB'
s.render.fps=30
s.camera=bpy.data.objects["SquatThreeQuarter"]
s.render.filepath=str(OUT/"_frames"/"squat_")
s.frame_start=1;s.frame_end=120
print("SQUAT_RENDER_START",s.frame_start,s.frame_end,flush=True)
bpy.ops.render.render(animation=True)
print("SQUAT_RENDER_COMPLETE",flush=True)
