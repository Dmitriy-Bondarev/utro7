#!/usr/bin/env python3
"""Validate the single-trainer G1 development artefacts without external packages.

This proves file/metadata consistency and unapproved-video gating only.
Biomechanical correctness still requires specialist and user review.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
reg=json.loads((ROOT/"content/motion/registry.json").read_text(encoding="utf-8"))
exercise=json.loads((ROOT/"content/exercises/EX-03-pushup.ru.json").read_text(encoding="utf-8"))
old=json.loads((ROOT/"docs/implementation/rejected_pushup_rig_audit.json").read_text(encoding="utf-8"))
new=json.loads((ROOT/"docs/implementation/candidate_pushup_rig_audit.json").read_text(encoding="utf-8"))

assert reg["schemaVersion"] == 1
assert all(item["status"] != "approved" for item in reg["assets"]), "Unexpected approved motion!"
assert sum(item["status"] == "rejected" for item in reg["assets"]) >= 3
assert exercise["id"] == "pushup"
assert exercise["motionStatus"] == "rejected" and exercise["acceptedVideo"] is None
assert [p["id"] for p in exercise["poseSheet"]] == [f"P{i}" for i in range(6)]
assert len(exercise["cameras"]) == 3
assert all(value is False for k,value in exercise["acceptance"].items() if k not in ("reviewer","reviewedAt"))
assert exercise["acceptance"]["reviewer"] is None
assert old["status"] == "REJECTED_FOR_INSTRUCTION"
assert new["status"] == "CANDIDATE_REVIEW_REQUIRED"
assert new["manualReviewRequired"] is True
assert len(old["failures"]) >= 4
assert not new["failures"], [item["reason"] for item in new["failures"]]
assert all(item["passed"] for item in new["checks"])
assert (ROOT/"assets/motion/quality-v3/trainer-female-pushup-static-v3.blend").is_file()
assert (ROOT/"assets/motion/quality-v3/pushup-pose-sheet-v3.jpg").is_file()
assert (ROOT/"preview/pushup-v3/index.html").is_file()

for camera in ("A_side","B_three_quarter","C_front"):
    for i in range(6):
        file=ROOT/"assets/motion/quality-v3/review"/f"{camera}_P{i}.jpg"
        assert file.stat().st_size > 1000, str(file)

preview=(ROOT/"preview/pushup-v3/index.html").read_text(encoding="utf-8")
assert "требуется визуальная и профессиональная приёмка" in preview
assert "не готовая учебная анимация" in preview
main=(ROOT/"index.html").read_text(encoding="utf-8")
assert "motion-policy.js" in main and "motion-blocked" in main
assert "renderedMotionKeys" not in main

print("PASS G1: 6 poses x 3 cameras; 12 candidate diagnostics PASS; candidate IN REVIEW")
print("PASS SAFETY: old push-up video REJECTED; no motion asset published as instructional")
print("NOTE: expert movement validation, user acceptance and physical iPhone QA PENDING")
