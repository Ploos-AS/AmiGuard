#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys

EICAR_SIZE = 68
EICAR_SHA256 = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
EICAR_PUBLISHER = "EICAR e.V."
EICAR_REFERENCE = "https://www.eicar.org/download-anti-malware-testfile/"


def qualify(path, source_url, retrieved_at):
    with open(path, "rb") as handle:
        data = handle.read()

    size = len(data)
    sha256 = hashlib.sha256(data).hexdigest()
    exact = size == EICAR_SIZE and sha256 == EICAR_SHA256

    return {
        "schema": 1,
        "kind": "amiguard-safe-test-acquisition",
        "id": "eicar-standard-av-test",
        "publisher": EICAR_PUBLISHER,
        "reference_url": EICAR_REFERENCE,
        "source_url": source_url,
        "retrieved_at": retrieved_at,
        "filename": os.path.basename(path),
        "size": size,
        "sha256": sha256,
        "expected_size": EICAR_SIZE,
        "expected_sha256": EICAR_SHA256,
        "exact_standard_file": exact,
        "malware_claim": False,
        "native_activation": False,
        "usage_note": "EICAR explicitly provides the test file for antivirus testing and describes it as safe/non-viral.",
        "repository_redistribution": "not-assumed; acquisition record only",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Qualify a locally acquired canonical 68-byte EICAR test file without activating a native AmiGuard signature."
    )
    parser.add_argument("path")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--retrieved-at", required=True,
                        help="Retrieval timestamp/date recorded by the operator")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = qualify(args.path, args.source_url, args.retrieved_at)
    except OSError as exc:
        print("EICAR acquisition qualifier: %s" % exc, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EICAR acquisition qualification")
        print("file: %s" % report["filename"])
        print("size: %d" % report["size"])
        print("sha256: %s" % report["sha256"])
        print("exact canonical 68-byte file: %s" %
              ("PASS" if report["exact_standard_file"] else "FAIL"))

    return 0 if report["exact_standard_file"] else 1


if __name__ == "__main__":
    sys.exit(main())
