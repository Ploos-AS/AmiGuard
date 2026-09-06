#!/usr/bin/env python3
"""Create a provenance-rich known-clean bootblock entry from a local image.

This tool is read-only with respect to the input media. It emits JSON to stdout
and never edits the repository database automatically.
"""

import argparse
import hashlib
import json
import os
import sys

BOOTBLOCK_SIZE = 1024


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_bootblock(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) < BOOTBLOCK_SIZE:
        raise ValueError("input is shorter than 1024 bytes")
    return raw[:BOOTBLOCK_SIZE], len(raw), sha256(raw)


def checksum_valid(data):
    total = 0
    for offset in range(0, BOOTBLOCK_SIZE, 4):
        word = int.from_bytes(data[offset:offset + 4], "big")
        previous = total
        total = (total + word) & 0xffffffff
        if total < previous:
            total = (total + 1) & 0xffffffff
    return total == 0xffffffff


def dos_type(data):
    if data[0:3] == b"DOS" and data[3] <= 7:
        return "DOS%d" % data[3]
    return None


def build_entry(args, bootblock, input_size, input_sha256):
    if not args.source.strip():
        raise ValueError("source is required")
    if not args.provenance.strip():
        raise ValueError("provenance is required")
    if args.status == "verified-clean" and not args.verifier.strip():
        raise ValueError("verified-clean requires --verifier")

    return {
        "id": args.entry_id,
        "name": args.name,
        "bootblock_sha256": sha256(bootblock),
        "dos_type": dos_type(bootblock),
        "checksum_valid": checksum_valid(bootblock),
        "status": args.status,
        "source": args.source,
        "provenance": args.provenance,
        "verification": args.verifier or None,
        "input": {
            "basename": os.path.basename(args.input),
            "size": input_size,
            "sha256": input_sha256,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Emit a provenance-rich AmiGuard known-clean bootblock entry")
    parser.add_argument("input", help="raw bootblock or disk image")
    parser.add_argument("--id", dest="entry_id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--status", choices=("candidate-clean", "verified-clean"),
                        default="candidate-clean")
    parser.add_argument("--source", required=True,
                        help="human-readable source reference")
    parser.add_argument("--provenance", required=True,
                        help="how this exact media/image was obtained and preserved")
    parser.add_argument("--verifier", default="",
                        help="independent clean verification evidence; required for verified-clean")
    args = parser.parse_args(argv)

    try:
        bootblock, input_size, input_sha256 = load_bootblock(args.input)
        entry = build_entry(args, bootblock, input_size, input_sha256)
    except (OSError, ValueError) as exc:
        print("known-clean importer: %s" % exc, file=sys.stderr)
        return 2

    print(json.dumps(entry, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
