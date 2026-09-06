#!/usr/bin/env python3
"""Validate evidence required before promoting an AmiGuard signature to verified.

This tool never reads malware unless the caller explicitly points it at a local
sample file, never modifies that file, and never edits repository metadata.
"""

import argparse
import hashlib
import json
import os
import sys

BOOTBLOCK_SIZE = 1024


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_bootblock(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) < BOOTBLOCK_SIZE:
        raise ValueError("input is shorter than 1024 bytes")
    return raw[:BOOTBLOCK_SIZE]


def match_signature(data, offset, pattern, mask):
    end = offset + len(pattern)
    if offset < 0 or end > len(data):
        return False
    for index in range(len(pattern)):
        if (data[offset + index] & mask[index]) != (pattern[index] & mask[index]):
            return False
    return True


def load_manifest(path):
    with open(path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("schema") != 1:
        raise ValueError("unsupported clean manifest schema")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("clean manifest requires at least one entry")
    return entries


def parse_hex(value, label):
    try:
        raw = bytes.fromhex(value)
    except ValueError:
        raise ValueError("%s must be hex" % label)
    if not raw:
        raise ValueError("%s must not be empty" % label)
    return raw


def qualify(sample_path, clean_manifest, offset, pattern_hex, mask_hex):
    pattern = parse_hex(pattern_hex, "pattern")
    mask = parse_hex(mask_hex, "mask")
    if len(pattern) != len(mask):
        raise ValueError("pattern and mask lengths differ")

    sample = read_bootblock(sample_path)
    positive = match_signature(sample, offset, pattern, mask)

    clean_results = []
    clean_ok = True
    for entry in load_manifest(clean_manifest):
        path = entry.get("path")
        expected = entry.get("bootblock_sha256")
        if not isinstance(path, str) or not path:
            raise ValueError("clean manifest entry missing path")
        clean = read_bootblock(path)
        actual_hash = sha256(clean)
        hash_ok = expected is None or expected == actual_hash
        matched = match_signature(clean, offset, pattern, mask)
        if not hash_ok or matched:
            clean_ok = False
        clean_results.append({
            "path": os.path.abspath(path),
            "bootblock_sha256": actual_hash,
            "expected_hash_ok": hash_ok,
            "signature_match": matched,
        })

    return {
        "sample_path": os.path.abspath(sample_path),
        "sample_bootblock_sha256": sha256(sample),
        "offset": offset,
        "pattern": pattern_hex.lower(),
        "mask": mask_hex.lower(),
        "positive_match": positive,
        "clean_regression_pass": clean_ok,
        "clean_results": clean_results,
        "qualified": positive and clean_ok,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="AmiGuard signature qualification gate")
    parser.add_argument("sample", help="isolated local malware sample or disk image")
    parser.add_argument("--clean-manifest", required=True)
    parser.add_argument("--offset", required=True, type=int)
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--mask", required=True)
    args = parser.parse_args(argv)

    try:
        report = qualify(args.sample, args.clean_manifest, args.offset,
                         args.pattern, args.mask)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("signature qualifier: %s" % exc, file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["qualified"] else 1


if __name__ == "__main__":
    sys.exit(main())
