#!/usr/bin/env python3
"""Release-blocking quality checks for the unapproved single-exercise G2 candidate."""
import json
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[2]
base=root/"assets/motion/quality-g2"
motion=json.loads((root/"docs/implementation/g2_pushup_motion_audit.json").read_text(encoding="utf-8"))
registry=json.loads((root/"content/motion/registry.json").read_text(encoding="utf-8"))
asset=next(x for x in registry["assets"] if x.get("rigId")=="mpfb-game-engine-53-bones-g2-v1")

assert motion["status"]=="CANDIDATE_NOT_APPROVED"
assert motion["frameCount"]==96
assert motion["fps"]==30
assert len(motion["checks"])==12
assert all(motion["checks"].values())
assert not motion["failed"]
assert asset["status"]=="review" and asset["review"] is None
assert not any(x["status"]=="approved" for x in registry["assets"])
assert (root/"assets/motion/quality-v3/trainer-female-pushup-static-v3.blend").stat().st_size>1000000
assert (root/"tools/blender/build_pushup_motion_candidate.py").is_file()
assert (base/"female-pushup-motion-sheet.jpg").stat().st_size>1000
assert (base/"female-pushup-candidate-poster.jpg").stat().st_size>1000
assert (root/"preview/pushup-g2/index.html").is_file()
assert "Не принято" in (root/"preview/pushup-g2/index.html").read_text(encoding="utf-8")

media=base/"female-pushup-candidate.mp4"
probe=subprocess.run(["ffprobe","-v","error","-show_entries",
 "stream=codec_name,codec_type,width,height,r_frame_rate",
 "-show_entries","format=duration","-of","json",str(media)],
 capture_output=True,text=True,check=True)
info=json.loads(probe.stdout)
streams=info["streams"]
videos=[s for s in streams if s.get("codec_type")=="video"]
assert len(videos)==1 and not [s for s in streams if s.get("codec_type")=="audio"]
assert all(videos[0][key]==value for key,value in {
 "codec_name":"h264","width":960,"height":600,"r_frame_rate":"30/1"}.items())
assert abs(float(info["format"]["duration"])-3.2)<.03

# Decode repeated loops, catching broken MP4 or bad stream termination.
decode=subprocess.run(["ffmpeg","-hide_banner","-v","error","-stream_loop","2",
 "-i",str(media),"-f","null","-"],capture_output=True,text=True)
assert decode.returncode==0,decode.stderr
print("PASS G2: 96 frames @30fps; 12/12 geometric checks; 3.2s silent H.264 960x600")
print("PASS G2: repeated MP4 decode; no approved 3D video leaked into live player")
print("LIMITATION: model anatomy / sports technique / real iPhone Safari NOT APPROVED")
