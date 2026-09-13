#!/usr/bin/env python3
"""Finalize a qualified AmiGuard file signature after native runtime evidence."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compile_file_signatures


def finalize(item, runtime_evidence):
    compile_file_signatures.validate("qualified file-signature draft", item)
    if item["status"] != "qualified":
        raise ValueError("file-signature finalization requires status=qualified")
    if item["kind"] != "file":
        raise ValueError("file-signature finalization requires kind=file")
    if item.get("synthetic"):
        raise ValueError("verified malware signatures must not be synthetic")
    if not isinstance(runtime_evidence, dict) or not runtime_evidence:
        raise ValueError("runtime evidence must be a non-empty object")
    if runtime_evidence.get("result") != "pass":
        raise ValueError("runtime evidence requires result=pass")
    if runtime_evidence.get("signature_id") != item["id"]:
        raise ValueError("runtime evidence signature_id does not match qualified proposal")
    if runtime_evidence.get("sample_sha256") != item["sample_sha256"]:
        raise ValueError("runtime evidence sample_sha256 does not match qualified proposal")
    for key in ("platform", "os", "cpu", "evidence"):
        value = runtime_evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("runtime evidence requires %s" % key)

    verified = dict(item)
    verified["status"] = "verified"
    provenance = dict(item["provenance"])
    provenance["runtime_verification"] = runtime_evidence
    verified["provenance"] = provenance
    verified.pop("candidate_is_verified_signature", None)
    verified.pop("malware_claim", None)
    verified.pop("native_activation", None)
    verified.pop("requires_visible_native_runtime", None)
    compile_file_signatures.validate("verified file-signature draft", verified)
    return verified


def main(argv=None):
    parser = argparse.ArgumentParser(description="Finalize a qualified AmiGuard file signature after native runtime PASS")
    parser.add_argument("qualified", help="qualified file-signature JSON draft")
    parser.add_argument("--runtime-evidence", required=True, help="JSON file containing native runtime verification evidence")
    parser.add_argument("-o", "--output", help="write verified JSON draft to this path")
    args = parser.parse_args(argv)
    try:
        with open(args.qualified, "r", encoding="utf-8") as handle:
            item = json.load(handle)
        with open(args.runtime_evidence, "r", encoding="utf-8") as handle:
            evidence = json.load(handle)
        verified = finalize(item, evidence)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("file-signature finalization: %s" % exc, file=sys.stderr)
        return 1

    rendered = json.dumps(verified, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except OSError as exc:
            print("file-signature finalization: %s" % exc, file=sys.stderr)
            return 1
        print("Wrote verified file-signature draft to %s" % args.output)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
