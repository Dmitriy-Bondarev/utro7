#!/usr/bin/env python3
"""Generate the browser-readable publication registry from content/motion/registry.json.

Run: python3 tools/dev/build_motion_policy.py
Check: python3 tools/dev/build_motion_policy.py --check
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "content/motion/registry.json"
TARGET = ROOT / "src/motion/motion-policy.js"
STATUSES = {"prototype", "rejected", "review", "approved"}
REQUIRED_APPROVALS = ("techniqueApproved", "visualApproved", "iphoneApproved", "rightsChecked")


def validate(document):
    assert document.get("schemaVersion") == 1
    keys = set()
    for entry in document["assets"]:
        assert entry.get("status") in STATUSES, entry
        key = (entry.get("exerciseId"), entry.get("trainerId"), entry.get("rigId"))
        assert all(key) and key not in keys, key
        keys.add(key)
        assert entry.get("video", "").startswith("./assets/motion/"), entry
        assert entry.get("poster", "").startswith("./assets/motion/"), entry
        if entry["status"] == "approved":
            review = entry.get("review")
            assert review and all(review.get(x) is True for x in REQUIRED_APPROVALS), entry
            assert review.get("reviewer") and review.get("reviewedAt"), entry
            assert len(entry.get("sha256", "")) == 64, entry
            media=ROOT/entry["video"].removeprefix("./")
            assert media.is_file() and hashlib.sha256(media.read_bytes()).hexdigest()==entry["sha256"], entry
        else:
            assert not entry.get("review") or entry["review"].get("techniqueApproved") is not True, entry


def bundle(document):
    literal = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
    return (
        "// GENERATED: content/motion/registry.json — edit JSON, not this file.\n"
        "(function (root) {\n"
        "  'use strict';\n"
        "  const registry = " + literal + ";\n"
        "  const required = ['techniqueApproved','visualApproved','iphoneApproved','rightsChecked'];\n"
        "  function approved(entry) {\n"
        "    const review = entry && entry.review;\n"
        "    return !!(entry && entry.status === 'approved' && review &&\n"
        "      required.every(key => review[key] === true) &&\n"
        "      typeof review.reviewer === 'string' && review.reviewer.trim() &&\n"
        "      typeof review.reviewedAt === 'string' && review.reviewedAt.trim() &&\n"
        "      /^[0-9a-f]{64}$/i.test(entry.sha256 || ''));\n"
        "  }\n"
        "  const api = {\n"
        "    schemaVersion: registry.schemaVersion,\n"
        "    getApproved(exerciseId, trainerId) {\n"
        "      return registry.assets.find(asset => asset.exerciseId === exerciseId &&\n"
        "        asset.trainerId === trainerId && approved(asset)) || null;\n"
        "    },\n"
        "    getStatus(exerciseId, trainerId) {\n"
        "      const found = registry.assets.filter(asset => asset.exerciseId === exerciseId && asset.trainerId === trainerId);\n"
        "      return found.some(item => item.status === 'rejected') ? 'rejected' :\n"
        "        found.some(item => item.status === 'review') ? 'review' :\n"
        "        found.some(item => item.status === 'prototype') ? 'prototype' : 'not_produced';\n"
        "    },\n"
        "    all() { return registry.assets.map(item => ({...item})); }\n"
        "  };\n"
        "  root.Utro7MotionPolicy = Object.freeze(api);\n"
        "})(typeof window === 'undefined' ? globalThis : window);\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = json.loads(SOURCE.read_text(encoding="utf-8"))
    validate(document)
    generated = bundle(document)
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != generated:
            raise SystemExit("FAIL: motion-policy.js is stale; run build_motion_policy.py")
        print("PASS: generated motion policy is up-to-date")
    else:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(generated, encoding="utf-8")
        print(f"Generated {TARGET} ({len(document['assets'])} registered assets)")


if __name__ == "__main__":
    main()
