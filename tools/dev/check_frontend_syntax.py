#!/usr/bin/env python3
"""Check extracted inline app JavaScript and service worker with Node.js."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
html=(root/"index.html").read_text(encoding="utf-8")
a=html.index("<script>\n  (()=>")+len("<script>")
b=html.index("</script>",a)
inline=html[a:b]

with tempfile.TemporaryDirectory(prefix="utro7-js-check-") as folder:
    script=Path(folder)/"index-inline.js"
    script.write_text(inline,encoding="utf-8")
    for candidate in (script,root/"src/motion/motion-policy.js",root/"sw.js"):
        subprocess.run(["node","--check",str(candidate)],check=True)
        print("PASS JS",candidate.name)
