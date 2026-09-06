#!/usr/bin/env python3
"""Read-only local bootblock analysis for AmiGuard research.

This tool never modifies its input and never promotes a signature to verified.
It accepts either a raw 1024-byte bootblock or a larger disk image whose first
1024 bytes contain the bootblock.
"""

import argparse
import hashlib
import json
import os
import string
import sys

BOOTBLOCK_SIZE = 1024
PRINTABLE = set(ord(ch) for ch in string.printable if ch not in "\r\n\t\x0b\x0c")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def checksum_valid(data):
    if len(data) != BOOTBLOCK_SIZE:
        return False
    total = 0
    for offset in range(0, BOOTBLOCK_SIZE, 4):
        word = int.from_bytes(data[offset:offset + 4], "big")
        previous = total
        total = (total + word) & 0xffffffff
        if total < previous:
            total = (total + 1) & 0xffffffff
    return total == 0xffffffff


def dos_type(data):
    if len(data) >= 4 and data[0:3] == b"DOS" and data[3] <= 7:
        return "DOS%d" % data[3]
    return None


def extract_strings(data, minimum=4):
    found = []
    start = None
    for index, value in enumerate(data + b"\x00"):
        if value in PRINTABLE:
            if start is None:
                start = index
        elif start is not None:
            if index - start >= minimum:
                found.append({
                    "offset": start,
                    "length": index - start,
                    "text": data[start:index].decode("ascii", "replace"),
                })
            start = None
    return found


def analyze(path, minimum_string=4):
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) < BOOTBLOCK_SIZE:
        raise ValueError("input is shorter than 1024 bytes")

    bootblock = raw[:BOOTBLOCK_SIZE]
    return {
        "path": os.path.abspath(path),
        "input_size": len(raw),
        "input_sha256": sha256(raw),
        "bootblock_size": BOOTBLOCK_SIZE,
        "bootblock_sha256": sha256(bootblock),
        "dos_type": dos_type(bootblock),
        "checksum_valid": checksum_valid(bootblock),
        "strings": extract_strings(bootblock, minimum_string),
    }


def research_draft(report, signature_id, name, family, source_reference):
    return {
        "schema": 1,
        "id": signature_id,
        "name": name,
        "family": family,
        "kind": "bootblock",
        "status": "research",
        "synthetic": False,
        "source": {
            "reference": source_reference,
        },
        "provenance": {
            "method": "local isolated sample analysis",
            "input_sha256": report["input_sha256"],
            "bootblock_sha256": report["bootblock_sha256"],
            "note": "Research only. Signature bytes/offset require independent verification before qualification.",
        },
        "sample_sha256": None,
        "signature": None,
        "verifier": "pending",
        "cleaner": "none",
    }


def print_text(report):
    print("Input: %s" % report["path"])
    print("Input size: %d bytes" % report["input_size"])
    print("Input SHA-256: %s" % report["input_sha256"])
    print("Bootblock SHA-256: %s" % report["bootblock_sha256"])
    print("DOS type: %s" % (report["dos_type"] or "custom/unknown"))
    print("Checksum: %s" % ("valid" if report["checksum_valid"] else "invalid/non-standard"))
    print("Printable strings:")
    if not report["strings"]:
        print("  (none)")
    for item in report["strings"]:
        print("  0x%03x  %s" % (item["offset"], item["text"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only AmiGuard bootblock research analyzer")
    parser.add_argument("input", help="raw 1024-byte bootblock or disk image")
    parser.add_argument("--json", action="store_true", help="print machine-readable analysis JSON")
    parser.add_argument("--min-string", type=int, default=4, help="minimum printable string length (default: 4)")
    parser.add_argument("--draft", action="store_true", help="emit a research metadata draft instead of analysis")
    parser.add_argument("--id", dest="signature_id")
    parser.add_argument("--name")
    parser.add_argument("--family")
    parser.add_argument("--source", default="local isolated sample")
    args = parser.parse_args(argv)

    if args.min_string < 1:
        parser.error("--min-string must be at least 1")
    if args.draft and not all((args.signature_id, args.name, args.family)):
        parser.error("--draft requires --id, --name, and --family")

    try:
        report = analyze(args.input, args.min_string)
    except (OSError, ValueError) as exc:
        print("bootblock analyzer: %s" % exc, file=sys.stderr)
        return 1

    if args.draft:
        print(json.dumps(research_draft(report, args.signature_id, args.name,
                                        args.family, args.source), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
