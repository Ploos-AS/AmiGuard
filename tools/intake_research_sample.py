#!/usr/bin/env python3
"""Create read-only research metadata for a local sample artifact.

The sample bytes are never copied into the repository or into the output JSON.
This tool only hashes and describes an operator-supplied local artifact. The
result is research evidence, not a malware verdict and not native activation.
"""

import argparse
import hashlib
import json
import os
import sys


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def validate_sha256(value):
    if value is None:
        return None
    if len(value) != 64:
        raise ValueError("expected SHA-256 must contain 64 hex characters")
    try:
        int(value, 16)
    except ValueError:
        raise ValueError("expected SHA-256 must contain 64 hex characters")
    return value.lower()


def intake(sample_path, source, provenance, expected_sha256=None, label=None):
    if not source.strip():
        raise ValueError("source must not be empty")
    if not provenance.strip():
        raise ValueError("provenance must not be empty")
    if os.path.islink(sample_path):
        raise ValueError("sample path must not be a symbolic link")
    if not os.path.isfile(sample_path):
        raise ValueError("sample is not a regular file")

    expected = validate_sha256(expected_sha256)
    size_before = os.path.getsize(sample_path)
    digest_before = sha256_file(sample_path)
    size_after = os.path.getsize(sample_path)
    digest_after = sha256_file(sample_path)
    if size_before != size_after or digest_before != digest_after:
        raise ValueError("sample changed during read-only intake")
    if expected is not None and digest_before != expected:
        raise ValueError("sample SHA-256 does not match expected SHA-256")

    return {
        "schema": 1,
        "kind": "amiguard-research-sample-intake",
        "status": "research",
        "sample_basename": os.path.basename(sample_path),
        "label": label,
        "size": size_before,
        "sha256": digest_before,
        "source": source,
        "provenance": provenance,
        "read_only_integrity_pass": True,
        "sample_bytes_embedded": False,
        "malware_claim": False,
        "native_activation": False,
        "cleaner": "none",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Create read-only AmiGuard research metadata for a local sample")
    parser.add_argument("sample")
    parser.add_argument("--source", required=True)
    parser.add_argument("--provenance", required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--label")
    parser.add_argument("-o", "--output")
    args = parser.parse_args(argv)

    try:
        report = intake(
            args.sample,
            args.source,
            args.provenance,
            expected_sha256=args.expected_sha256,
            label=args.label,
        )
    except (OSError, ValueError) as exc:
        print("research sample intake: %s" % exc, file=sys.stderr)
        return 2

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except OSError as exc:
            print("research sample intake: %s" % exc, file=sys.stderr)
            return 2
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
