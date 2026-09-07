#!/usr/bin/env python3
"""Preflight an AmiGuard safe-test proposal against local clean files.

This tool is read-only. It validates the safe-test metadata, confirms that the
proposed signature matches the positive artifact, then proves that no supplied
clean file matches the same signature. It does not edit repository metadata and
does not activate the signature natively.
"""

import argparse
import hashlib
import json
import os
import sys


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def read(path):
    with open(path, "rb") as handle:
        return handle.read()


def parse_signature(proposal):
    if proposal.get("schema") != 1:
        raise ValueError("unsupported proposal schema")
    if proposal.get("kind") != "file":
        raise ValueError("proposal must be kind=file")
    if proposal.get("status") != "safe-test":
        raise ValueError("proposal must be status=safe-test")
    if proposal.get("synthetic") is not False:
        raise ValueError("safe-test proposal must be non-synthetic")
    if proposal.get("cleaner") != "none":
        raise ValueError("safe-test proposal must not define a cleaner")
    safe = proposal.get("safe_test")
    if not isinstance(safe, dict) or safe.get("malware_claim") is not False:
        raise ValueError("proposal must explicitly state malware_claim=false")
    if safe.get("native_verdict") != "TEST-SIGNATURE":
        raise ValueError("safe-test native verdict must be TEST-SIGNATURE")

    sig = proposal.get("signature")
    if not isinstance(sig, dict):
        raise ValueError("proposal is missing signature")
    offset = sig.get("offset")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("invalid signature offset")
    try:
        pattern = bytes.fromhex(sig.get("bytes", ""))
        mask = bytes.fromhex(sig.get("mask", ""))
    except (TypeError, ValueError):
        raise ValueError("signature bytes/mask must be hex")
    if not pattern or len(pattern) != len(mask):
        raise ValueError("signature bytes/mask must be non-empty and equal length")
    return offset, pattern, mask


def matches(data, offset, pattern, mask):
    end = offset + len(pattern)
    if end > len(data):
        return False
    for index in range(len(pattern)):
        if (data[offset + index] & mask[index]) != (pattern[index] & mask[index]):
            return False
    return True


def preflight(proposal_path, positive_path, clean_paths):
    proposal = load_json(proposal_path)
    offset, pattern, mask = parse_signature(proposal)

    positive = read(positive_path)
    positive_hash = sha256(positive)
    expected_hash = proposal.get("sample_sha256")
    if positive_hash != expected_hash:
        raise ValueError("positive artifact SHA-256 does not match proposal")
    positive_match = matches(positive, offset, pattern, mask)

    clean_results = []
    clean_ok = True
    positive_real = os.path.realpath(positive_path)
    for path in clean_paths:
        if os.path.realpath(path) == positive_real:
            raise ValueError("positive artifact must not be included in clean corpus")
        data = read(path)
        matched = matches(data, offset, pattern, mask)
        if matched:
            clean_ok = False
        clean_results.append({
            "path": os.path.abspath(path),
            "size": len(data),
            "sha256": sha256(data),
            "signature_match": matched,
        })

    return {
        "schema": 1,
        "kind": "amiguard-safe-test-preflight",
        "id": proposal.get("id"),
        "proposal_status": "safe-test",
        "positive_path": os.path.abspath(positive_path),
        "positive_sha256": positive_hash,
        "positive_match": positive_match,
        "clean_files_tested": len(clean_results),
        "clean_regression_pass": clean_ok,
        "preflight_pass": positive_match and clean_ok and bool(clean_results),
        "malware_claim": False,
        "native_activation": False,
        "clean_results": clean_results,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preflight an AmiGuard safe-test against a local clean-file corpus")
    parser.add_argument("proposal")
    parser.add_argument("positive")
    parser.add_argument("clean", nargs="+")
    parser.add_argument("-o", "--output")
    args = parser.parse_args(argv)

    try:
        report = preflight(args.proposal, args.positive, args.clean)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("safe-test preflight: %s" % exc, file=sys.stderr)
        return 2

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except OSError as exc:
            print("safe-test preflight: %s" % exc, file=sys.stderr)
            return 2
    else:
        sys.stdout.write(rendered)
    return 0 if report["preflight_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
