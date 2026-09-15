#!/usr/bin/env python3
import argparse
import json
import re
import sys

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HEX_RE = re.compile(r"^[0-9a-fA-F]+$")
PRODUCERS = {"ASW", "AmiSandbox"}
KINDS = {"file", "bootblock", "disk-image", "memory-artifact"}


def fail(message):
    raise ValueError(message)


def validate(item):
    if not isinstance(item, dict):
        fail("handoff must be an object")
    if item.get("schema") != "amiguard-asw-handoff-v1":
        fail("unsupported schema")
    for key in ("handoff_id", "created_at", "producer", "sample", "analysis", "candidate"):
        if key not in item:
            fail("missing required field %s" % key)
    if not isinstance(item["handoff_id"], str) or not item["handoff_id"]:
        fail("invalid handoff_id")
    if not isinstance(item["created_at"], str) or "T" not in item["created_at"]:
        fail("invalid created_at")

    producer = item["producer"]
    if not isinstance(producer, dict) or producer.get("name") not in PRODUCERS:
        fail("producer must be ASW or AmiSandbox")
    if not isinstance(producer.get("version"), str) or not producer["version"]:
        fail("producer version required")

    sample = item["sample"]
    if not isinstance(sample, dict):
        fail("sample must be an object")
    if not isinstance(sample.get("sha256"), str) or not SHA256_RE.match(sample["sha256"]):
        fail("sample sha256 must be lowercase SHA-256")
    if not isinstance(sample.get("size"), int) or sample["size"] <= 0:
        fail("sample size must be positive")
    if sample.get("kind") not in KINDS:
        fail("invalid sample kind")
    if not isinstance(sample.get("redistributable"), bool):
        fail("sample redistributable must be boolean")

    analysis = item["analysis"]
    if not isinstance(analysis, dict) or analysis.get("result") not in {"candidate", "inconclusive", "clean"}:
        fail("invalid analysis result")
    evidence = analysis.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x for x in evidence):
        fail("analysis evidence must be a non-empty string list")

    candidate = item["candidate"]
    if analysis["result"] == "candidate" and candidate is None:
        fail("candidate analysis requires candidate signature proposal")
    if analysis["result"] != "candidate" and candidate is not None:
        fail("non-candidate analysis must not carry signature proposal")
    if candidate is not None:
        if not isinstance(candidate, dict) or candidate.get("kind") not in {"file", "bootblock"}:
            fail("candidate kind must be file or bootblock")
        if candidate["kind"] != sample["kind"]:
            fail("candidate kind must match sample kind")
        if not isinstance(candidate.get("offset"), int) or candidate["offset"] < 0:
            fail("invalid candidate offset")
        pattern = candidate.get("bytes")
        mask = candidate.get("mask")
        if not isinstance(pattern, str) or not pattern or len(pattern) % 2 or not HEX_RE.match(pattern):
            fail("candidate bytes must be even-length hex")
        if not isinstance(mask, str) or len(mask) != len(pattern) or not HEX_RE.match(mask):
            fail("candidate mask must exactly match candidate byte length")
    return True


def main():
    parser = argparse.ArgumentParser(description="Validate AmiGuard ASW/AmiSandbox handoff metadata")
    parser.add_argument("handoff")
    args = parser.parse_args()
    try:
        with open(args.handoff, "r", encoding="utf-8") as handle:
            item = json.load(handle)
        validate(item)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("ASW handoff: %s" % exc, file=sys.stderr)
        return 1
    print("ASW handoff metadata is valid. Review and AmiGuard qualification are still required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
