#!/usr/bin/env python3
"""Build a neutral review queue from AmiGuard corpus triage JSON."""

import argparse
import json
import sys


def build_queue(report):
    if report.get("schema") != 1 or report.get("kind") != "amiguard-bootblock-corpus-triage":
        raise ValueError("unsupported triage report")
    records = report.get("records")
    if not isinstance(records, list):
        raise ValueError("triage report records must be a list")

    grouped = {}
    for record in records:
        classification = record.get("classification")
        if classification not in ("STANDARD", "CUSTOM", "UNKNOWN"):
            raise ValueError("invalid classification")
        digest = record.get("bootblock_sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError("invalid bootblock_sha256")
        if classification == "STANDARD":
            continue
        group = grouped.setdefault(digest, {
            "bootblock_sha256": digest,
            "classification": classification,
            "reason_code": record.get("reason_code"),
            "occurrences": 0,
            "paths": [],
            "strings": [],
            "malware_claim": False,
        })
        if group["classification"] != classification or group["reason_code"] != record.get("reason_code"):
            raise ValueError("inconsistent records for bootblock %s" % digest)
        group["occurrences"] += 1
        group["paths"].append(record.get("path"))
        for item in record.get("strings", []):
            text = item.get("text") if isinstance(item, dict) else None
            if text and text not in group["strings"]:
                group["strings"].append(text)

    priority = {"CUSTOM": 0, "UNKNOWN": 1}
    items = sorted(grouped.values(), key=lambda item: (
        priority[item["classification"]],
        -item["occurrences"],
        item["bootblock_sha256"],
    ))
    for item in items:
        item["paths"] = sorted(item["paths"])
        item["strings"] = sorted(item["strings"])

    return {
        "schema": 1,
        "kind": "amiguard-bootblock-review-queue",
        "items": items,
        "item_count": len(items),
        "malware_claim": False,
        "policy": "priority is triage convenience only; it is not a malware verdict",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build AmiGuard bootblock review queue")
    parser.add_argument("triage_json")
    parser.add_argument("--json", action="store_true", help="print full queue JSON")
    args = parser.parse_args(argv)
    try:
        with open(args.triage_json, "r", encoding="utf-8") as handle:
            report = json.load(handle)
        queue = build_queue(report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("review queue: %s" % exc, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(queue, indent=2, sort_keys=True))
    else:
        print("Review items: %d" % queue["item_count"])
        for index, item in enumerate(queue["items"], 1):
            print("%d. %s %s x%d" % (index, item["classification"],
                                      item["bootblock_sha256"], item["occurrences"]))
        print("Malware claim: no")
    return 0


if __name__ == "__main__":
    sys.exit(main())
