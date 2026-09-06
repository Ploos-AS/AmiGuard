#!/usr/bin/env python3
"""Batch, read-only bootblock triage for local AmiGuard research corpora."""

import argparse
import json
import os
import sys

import analyze_bootblock


def collect_paths(inputs, recursive=False):
    paths = []
    for entry in inputs:
        if os.path.isfile(entry):
            paths.append(os.path.abspath(entry))
        elif os.path.isdir(entry):
            if recursive:
                for root, dirs, files in os.walk(entry):
                    dirs.sort()
                    for name in sorted(files):
                        paths.append(os.path.abspath(os.path.join(root, name)))
            else:
                for name in sorted(os.listdir(entry)):
                    path = os.path.join(entry, name)
                    if os.path.isfile(path):
                        paths.append(os.path.abspath(path))
        else:
            raise ValueError("input path does not exist: %s" % entry)
    return sorted(set(paths))


def triage(inputs, recursive=False, minimum_string=4):
    paths = collect_paths(inputs, recursive)
    if not paths:
        raise ValueError("no input files found")

    records = []
    errors = []
    unique = {}
    counts = {"STANDARD": 0, "CUSTOM": 0, "UNKNOWN": 0}

    for path in paths:
        try:
            report = analyze_bootblock.analyze(path, minimum_string)
        except (OSError, ValueError) as exc:
            errors.append({"path": path, "error": str(exc)})
            continue

        record = {
            "path": report["path"],
            "input_size": report["input_size"],
            "input_sha256": report["input_sha256"],
            "bootblock_sha256": report["bootblock_sha256"],
            "dos_type": report["dos_type"],
            "checksum_valid": report["checksum_valid"],
            "classification": report["classification"],
            "reason_code": report["reason_code"],
            "malware_claim": False,
            "strings": report["strings"],
        }
        records.append(record)
        counts[record["classification"]] += 1
        unique.setdefault(record["bootblock_sha256"], []).append(record["path"])

    duplicates = []
    for digest in sorted(unique):
        if len(unique[digest]) > 1:
            duplicates.append({
                "bootblock_sha256": digest,
                "occurrences": len(unique[digest]),
                "paths": sorted(unique[digest]),
            })

    return {
        "schema": 1,
        "kind": "amiguard-bootblock-corpus-triage",
        "files_seen": len(paths),
        "files_analyzed": len(records),
        "files_failed": len(errors),
        "unique_bootblocks": len(unique),
        "classification_counts": counts,
        "malware_claim": False,
        "records": records,
        "duplicates": duplicates,
        "errors": errors,
    }


def print_text(report):
    print("Files seen: %d" % report["files_seen"])
    print("Analyzed: %d" % report["files_analyzed"])
    print("Failed: %d" % report["files_failed"])
    print("Unique bootblocks: %d" % report["unique_bootblocks"])
    print("STANDARD: %d" % report["classification_counts"]["STANDARD"])
    print("CUSTOM: %d" % report["classification_counts"]["CUSTOM"])
    print("UNKNOWN: %d" % report["classification_counts"]["UNKNOWN"])
    print("Duplicate groups: %d" % len(report["duplicates"]))
    print("Malware claim: no")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only AmiGuard batch bootblock corpus triage")
    parser.add_argument("input", nargs="+", help="files and/or directories")
    parser.add_argument("--recursive", action="store_true", help="recurse into input directories")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--min-string", type=int, default=4,
                        help="minimum printable string length (default: 4)")
    args = parser.parse_args(argv)

    if args.min_string < 1:
        parser.error("--min-string must be at least 1")

    try:
        report = triage(args.input, args.recursive, args.min_string)
    except (OSError, ValueError) as exc:
        print("corpus triage: %s" % exc, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
