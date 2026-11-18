"""Minimal CI contract for the master-trainer program.

Does not certify visual fidelity, anatomy or rights. It prevents silently
marking a missing, unreviewed or unlicensed asset 'accepted'.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
docs=[
    "docs/UTRO7_MASTER_TRAINER_TZ.md",
    "docs/TRAINER_MASTER_ACCEPTANCE_CHECKLIST.md",
    "docs/implementation/TRAINER_PIPELINE_EVALUATION.md",
    "docs/implementation/TRAINER_MASTER_STATUS.md",
    "tools/blender/trainer_master/create_studio.py",
    "tools/blender/trainer_master/validate_studio.py",
    "assets/trainer_master/scenes/utro7_studio_template.blend",
]
for p in docs:
    path=ROOT/p
    assert path.is_file() and path.stat().st_size>100, p

m=json.loads((ROOT/"assets/trainer_master/master_manifest.json").read_text(encoding="utf-8"))
assert m["schemaVersion"]==1
assert m["assetId"]=="trainer_female_master_01"
assert m["version"]=="v1"
assert m["milestone"] in {
    "T0_SOURCE_REVIEW","T1_VISUAL_REVIEW","T2_RIG_REVIEW",
    "T3_POSE_REVIEW","T4_MASTER_RELEASE"
}
assert len(m["reviewRenderIds"])==7 and len(set(m["reviewRenderIds"]))==7
assert len(m["requiredPoseIds"])==8 and len(set(m["requiredPoseIds"]))==8
flags=("masterModelAvailable","visualApproved","rigApproved","posesApproved","rightsReviewed")
assert all(type(m[k]) is bool for k in flags)
if not m["masterModelAvailable"]:
    assert not m["visualApproved"] and not m["rigApproved"] and not m["posesApproved"]
    assert m["sourceFile"] is None and m["modelScene"] is None
if m["status"]=="accepted":
    assert all(m[k] for k in flags), "Master acceptance requires ALL gates."
    assert m["sourceVendor"] and m["sourceAssetLicense"] and m["modelScene"]
    assert m.get("userAcceptanceVerdict")=="accepted"
else:
    assert m.get("userAcceptanceVerdict")!="accepted"

doc=(ROOT/"docs/TRAINER_MASTER_ACCEPTANCE_CHECKLIST.md").read_text(encoding="utf-8")
for id_ in m["reviewRenderIds"]:
    review_id="-".join(id_.split("_")[:2])
    assert review_id in doc, f"Render acceptance missing: {review_id}"
for id_ in m["requiredPoseIds"]:
    assert id_ in doc, f"Pose acceptance missing: {id_}"
assert "NOT STARTED" in doc

print("PASS TRAINER CONTRACT: 7 render views, 8 pose IDs, source status",m["milestone"])
print("PASS ACCEPTANCE SAFETY: no unreviewed master asset promoted to accepted")
print("NOTE: Visual fidelity is user-reviewed, never automated.")
