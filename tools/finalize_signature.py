#!/usr/bin/env python3
"""Finalize an AmiGuard qualified signature to verified after native runtime evidence.

The tool is side-effect-free: it reads a qualified metadata draft and explicit
runtime evidence, validates both, and emits a verified JSON record. It never
edits repository files automatically.
"""

import argparse
import json
import sys

import compile_signatures


def finalize(item, runtime_evidence):
    compile_signatures.validate("qualified draft", item)
    if item["status"] != "qualified":
        raise ValueError("finalization requires status=qualified")
    if not isinstance(runtime_evidence, dict) or not runtime_evidence:
        raise ValueError("runtime evidence must be a non-empty object")
    if runtime_evidence.get("result") != "pass":
        raise ValueError("runtime evidence requires result=pass")
    for key in ("platform", "os", "cpu", "evidence"):
        value = runtime_evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("runtime evidence requires %s" % key)

    verified = dict(item)
    verified["status"] = "verified"
    provenance = dict(item["provenance"])
    provenance["runtime_verification"] = runtime_evidence
    verified["provenance"] = provenance
    compile_signatures.validate("verified draft", verified)
    return verified


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Finalize an AmiGuard qualified signature after native runtime PASS")
    parser.add_argument("qualified", help="qualified signature JSON draft")
    parser.add_argument("--runtime-evidence", required=True,
                        help="JSON file containing native runtime verification evidence")
    parser.add_argument("-o", "--output", help="write verified JSON draft to this path")
    args = parser.parse_args(argv)

    try:
        with open(args.qualified, "r", encoding="utf-8") as handle:
            item = json.load(handle)
        with open(args.runtime_evidence, "r", encoding="utf-8") as handle:
            evidence = json.load(handle)
        verified = finalize(item, evidence)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("signature finalization: %s" % exc, file=sys.stderr)
        return 1

    rendered = json.dumps(verified, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except OSError as exc:
            print("signature finalization: %s" % exc, file=sys.stderr)
            return 1
        print("Wrote verified metadata draft to %s" % args.output)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
