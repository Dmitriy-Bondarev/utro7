#!/usr/bin/env python3
"""Validate all six original 3D MP4 exports are available and playable."""
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
base=ROOT/"assets/motion/v1"
records=[]
for avatar in ("woman","man"):
    for exercise in ("march","squat","pushup"):
        stem=avatar+"-"+exercise
        files={ext:base/(stem+"."+ext) for ext in ("mp4","jpg","blend")}
        assert all(path.is_file() and path.stat().st_size>100 for path in files.values()), stem
        r=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,codec_type,width,height,r_frame_rate",
          "-show_entries","format=duration,size","-of","json",str(files["mp4"])],capture_output=True,text=True,check=True)
        data=json.loads(r.stdout)
        video=[s for s in data["streams"] if s["codec_type"]=="video"]
        audio=[s for s in data["streams"] if s["codec_type"]=="audio"]
        assert len(video)==1 and not audio,stem+" audio must be absent"
        v=video[0]
        assert (v["codec_name"],v["width"],v["height"],v["r_frame_rate"])==("h264",560,560,"20/1"),stem
        duration=float(data["format"]["duration"])
        assert 1.95<=duration<=2.05,stem+" duration: "+str(duration)
        records.append(dict(name=stem,codec=v["codec_name"],duration=duration,size=files["mp4"].stat().st_size))
print(json.dumps({"result":"PASS","count":len(records),"media":records},ensure_ascii=False,indent=2))
