#!/usr/bin/env python3
"""Differentially qualify an M2.2n research candidate without activating it."""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path):
    return Path(path).read_bytes()


def load_json(path):
    return json.loads(Path(path).read_text())


def parse_review(path):
    review = load_json(path)
    if review.get("schema") != 1 or review.get("kind") != "amiguard-file-signature-candidate-review":
        raise ValueError("invalid M2.2n candidate review")
    if review.get("status") != "research-candidate":
        raise ValueError("candidate review must have status research-candidate")
    if review.get("candidate_is_verified_signature") is not False:
        raise ValueError("candidate review violates unverified contract")
    if review.get("malware_claim") is not False or review.get("native_activation") is not False:
        raise ValueError("candidate review violates neutral safety contract")
    candidate = review.get("candidate") or {}
    offset = candidate.get("offset")
    length = candidate.get("length")
    try:
        pattern = bytes.fromhex(candidate.get("hex", ""))
        mask = bytes.fromhex(candidate.get("mask", ""))
    except (TypeError, ValueError):
        raise ValueError("candidate hex/mask must be valid hex")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("candidate offset is invalid")
    if not isinstance(length, int) or length <= 0:
        raise ValueError("candidate length is invalid")
    if len(pattern) != length or len(mask) != length:
        raise ValueError("candidate length does not match hex/mask")
    sample = review.get("sample") or {}
    digest = sample.get("sha256")
    size = sample.get("size")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ValueError("candidate sample SHA-256 is invalid")
    if not isinstance(size, int) or size < 0:
        raise ValueError("candidate sample size is invalid")
    return review, offset, pattern, mask


def matches(data, offset, pattern, mask):
    if offset + len(pattern) > len(data):
        return False
    return all(
        (data[offset + i] & mask[i]) == (pattern[i] & mask[i])
        for i in range(len(pattern))
    )


def clean_paths_from_manifest(path):
    manifest = load_json(path)
    if manifest.get("schema") != 1 or manifest.get("kind") != "amiguard-clean-file-corpus":
        raise ValueError("invalid clean corpus manifest")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("clean corpus manifest must contain files")
    out = []
    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            raise ValueError("clean corpus entry %d is invalid" % index)
        p = entry.get("extracted_path")
        size = entry.get("size")
        digest = entry.get("sha256")
        if not isinstance(p, str) or not p:
            raise ValueError("clean corpus entry %d has no extracted_path" % index)
        if not isinstance(size, int) or size < 0:
            raise ValueError("clean corpus entry %d has invalid size" % index)
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest.lower()):
            raise ValueError("clean corpus entry %d has invalid SHA-256" % index)
        data = read_bytes(p)
        if len(data) != size:
            raise ValueError("clean corpus size mismatch: %s" % p)
        if sha256(data) != digest.lower():
            raise ValueError("clean corpus SHA-256 mismatch: %s" % p)
        out.append(p)
    return out


def merge_paths(explicit, from_manifests):
    out = []
    seen = set()
    for p in list(explicit) + list(from_manifests):
        real = os.path.realpath(p)
        if real not in seen:
            seen.add(real)
            out.append(p)
    return out


def qualify(review_path, positive_path, clean_paths):
    review, offset, pattern, mask = parse_review(review_path)
    positive = read_bytes(positive_path)
    positive_hash = sha256(positive)
    expected = review["sample"]
    if len(positive) != expected["size"]:
        raise ValueError("positive sample size does not match candidate review")
    if positive_hash != expected["sha256"]:
        raise ValueError("positive sample SHA-256 does not match candidate review")
    positive_match = matches(positive, offset, pattern, mask)

    positive_real = os.path.realpath(positive_path)
    collisions = []
    tested = 0
    for p in clean_paths:
        if os.path.realpath(p) == positive_real:
            raise ValueError("positive sample must not be included in clean corpus")
        data = read_bytes(p)
        tested += 1
        if matches(data, offset, pattern, mask):
            collisions.append({"sha256": sha256(data), "size": len(data), "basename": os.path.basename(p)})

    clean_pass = tested > 0 and not collisions
    qualified = positive_match and clean_pass
    return {
        "schema": 1,
        "kind": "amiguard-file-signature-candidate-qualification",
        "candidate_status": "research-candidate",
        "sample_sha256": positive_hash,
        "sample_size": len(positive),
        "positive_match": positive_match,
        "clean_files_tested": tested,
        "clean_collisions": collisions,
        "clean_regression_pass": clean_pass,
        "differential_qualification_pass": qualified,
        "candidate_is_verified_signature": False,
        "promotion_ready": False,
        "malware_claim": False,
        "native_activation": False,
        "cleaner": None,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Differentially qualify an M2.2n file-signature candidate")
    ap.add_argument("review")
    ap.add_argument("positive")
    ap.add_argument("clean", nargs="*")
    ap.add_argument("--clean-manifest", action="append", default=[])
    ap.add_argument("-o", "--output")
    args = ap.parse_args(argv)
    try:
        manifest_paths = []
        for path in args.clean_manifest:
            manifest_paths.extend(clean_paths_from_manifest(path))
        clean_paths = merge_paths(args.clean, manifest_paths)
        if not clean_paths:
            raise ValueError("at least one clean file or --clean-manifest is required")
        report = qualify(args.review, args.positive, clean_paths)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("candidate qualification: %s" % exc, file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)
    return 0 if report["differential_qualification_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
