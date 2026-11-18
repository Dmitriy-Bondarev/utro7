#!/usr/bin/env python3
"""Check the EX-04 squat review candidate: content, 9 geometric checks, video.

WARNING: technical validation only. No coach/user/iPhone approval inferred.
"""
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
data=json.loads((R/"content/exercises/EX-04-squat.ru.json").read_text())
reg=json.loads((R/"content/motion/registry.json").read_text())
audit=json.loads((R/"docs/implementation/squat_g1_geometry_audit.json").read_text())
assert data["id"]=="squat" and data["motionStatus"]=="review"
assert data["acceptedVideo"] is None
assert not data["acceptance"]["fitnessExpertApproved"]
assert not data["acceptance"]["visualAccepted"]
asset=next(x for x in reg["assets"] if x.get("rigId")=="mpfb-game-engine-53-bones-squat-g1")
assert asset["status"]=="review" and asset.get("review") is None
assert len(audit["checks"])==9 and all(audit["checks"].values())
mp4=R/"assets/motion/squat-g1/female-squat-candidate.mp4"
assert (R/"assets/motion/squat-g1/female-squat-poster.jpg").stat().st_size>1000
assert (R/"assets/motion/squat-g1/female-squat-motion-sheet.jpg").stat().st_size>1000
assert (R/"preview/squat-g1/index.html").is_file()
probe=json.loads(subprocess.run(
    ["ffprobe","-v","error","-show_entries","stream=codec_name,codec_type,width,height,avg_frame_rate",
     "-show_entries","format=duration","-of","json",str(mp4)],
    check=True,capture_output=True,text=True).stdout)
video=[s for s in probe["streams"] if s.get("codec_type")=="video"]
audio=[s for s in probe["streams"] if s.get("codec_type")=="audio"]
assert len(video)==1 and not audio
assert video[0]["codec_name"]=="h264"
assert video[0]["width"]==800 and video[0]["height"]==800
assert video[0]["avg_frame_rate"]=="30/1"
assert abs(float(probe["format"]["duration"])-4.0)<0.03
assert subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-stream_loop","2",
    "-i",str(mp4),"-f","null","-"],capture_output=True).returncode==0
print("PASS EX-04: 9/9 geometry checks; 120 frames / 30fps / 4s / 800x800 H.264")
print("PASS EX-04: 3 repeated silent MP4 loops decode; still REVIEW not approved")
print("NOTE: subjective fidelity, squat technique and real iPhone Safari QA pending")
