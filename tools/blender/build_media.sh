#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
BASE="assets/motion/v1"
mkdir -p "$BASE"
for avatar in woman man; do
  for exercise in march squat pushup; do
    name="${avatar}-${exercise}"
    echo "RENDERING $name"
    blender -b -t 6 -P tools/blender/render_motion.py -- --avatar "$avatar" --exercise "$exercise" --frames 40 --size 560 > "/tmp/utro7-render-${name}.log" 2>&1
    if ! grep -q "UTRO7_FRAMES_COMPLETE ${name}" "/tmp/utro7-render-${name}.log"; then
      tail -50 "/tmp/utro7-render-${name}.log"
      exit 2
    fi
    test -s "$BASE/_frames/$name/frame_0040.png"
    ffmpeg -hide_banner -loglevel error -y -framerate 20 -i "$BASE/_frames/$name/frame_%04d.png" -an \
      -c:v libx264 -pix_fmt yuv420p -profile:v main -level 3.1 -movflags +faststart -crf 23 \
      "$BASE/$name.mp4"
    ffmpeg -hide_banner -loglevel error -y -i "$BASE/$name.mp4" -frames:v 1 -q:v 3 "$BASE/$name.jpg"
    echo "RENDERED $name $(du -h "$BASE/$name.mp4" | cut -f1)"
  done
done
printf "\nAll six H.264 clips complete\n"
du -sh "$BASE"/*.mp4 "$BASE"/*.blend | tail -14
