#!/usr/bin/env python3
"""Generate a safe-test metadata proposal from acquisition evidence.

This tool is side-effect-free with respect to repository metadata. It requires
an exact acquisition report plus the exact locally acquired artifact, derives a
full-file fixed-offset signature from those bytes, and emits a `safe-test`
proposal. It never emits `verified` and never claims malware.
"""

import argparse
import hashlib
import json
import os
import sys

MAX_FILE_SIZE = 128 * 1024


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_safe_test(research, acquisition, artifact_path):
    if research.get("status") != "research":
        raise ValueError("source metadata must be status=research")
    if research.get("synthetic") is not False:
        raise ValueError("safe-test source must be non-synthetic")
    if research.get("kind") != "file":
        raise ValueError("safe-test source must be kind=file")

    if acquisition.get("schema") != 1 or acquisition.get("kind") != "amiguard-safe-test-acquisition":
        raise ValueError("invalid acquisition report")
    if acquisition.get("id") != research.get("id"):
        raise ValueError("acquisition id does not match research metadata")
    if acquisition.get("exact_standard_file") is not True:
        raise ValueError("acquisition report did not pass exact-file qualification")
    if acquisition.get("malware_claim") is not False:
        raise ValueError("acquisition report must not claim malware")
    if acquisition.get("native_activation") is not False:
        raise ValueError("acquisition report must precede native activation")

    with open(artifact_path, "rb") as handle:
        data = handle.read()
    if not data:
        raise ValueError("artifact is empty")
    if len(data) > MAX_FILE_SIZE:
        raise ValueError("artifact exceeds 128 KiB intake limit")

    actual_hash = sha256(data)
    if acquisition.get("size") != len(data):
        raise ValueError("artifact size does not match acquisition report")
    if acquisition.get("sha256") != actual_hash:
        raise ValueError("artifact SHA-256 does not match acquisition report")

    proposal = dict(research)
    proposal["status"] = "safe-test"
    proposal["sample_sha256"] = actual_hash
    proposal["signature"] = {
        "offset": 0,
        "bytes": data.hex(),
        "mask": "ff" * len(data),
    }
    proposal["verifier"] = "exact-safe-test-artifact"
    proposal["cleaner"] = "none"
    proposal["provenance"] = dict(research["provenance"])
    proposal["provenance"]["acquisition"] = {
        "publisher": acquisition.get("publisher"),
        "source_url": acquisition.get("source_url"),
        "retrieved_at": acquisition.get("retrieved_at"),
        "filename": acquisition.get("filename"),
        "size": len(data),
        "sha256": actual_hash,
    }
    proposal["provenance"]["signature_derivation"] = (
        "Exact full-file signature derived locally from the independently "
        "qualified harmless artifact; offset 0 with an all-0xff mask."
    )
    proposal["safe_test"] = {
        "malware_claim": False,
        "native_verdict": "TEST-SIGNATURE",
        "requires_clean_corpus_preflight": True,
        "requires_visible_runtime_qualification": True,
    }
    proposal.pop("research", None)
    return proposal


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate an AmiGuard safe-test metadata proposal")
    parser.add_argument("research_metadata")
    parser.add_argument("acquisition_report")
    parser.add_argument("artifact")
    parser.add_argument("-o", "--output")
    args = parser.parse_args(argv)

    try:
        proposal = build_safe_test(
            load_json(args.research_metadata),
            load_json(args.acquisition_report),
            args.artifact,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("safe-test promotion: %s" % exc, file=sys.stderr)
        return 1

    rendered = json.dumps(proposal, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except OSError as exc:
            print("safe-test promotion: %s" % exc, file=sys.stderr)
            return 1
        print("Wrote safe-test metadata proposal to %s" % args.output)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
