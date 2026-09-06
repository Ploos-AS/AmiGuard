#!/usr/bin/env python3
"""Generate a verified AmiGuard metadata draft after qualification passes.

This tool is intentionally local-only. It reads an isolated sample and a clean
manifest through qualify_signature, but it does not edit repository files and
never copies sample bytes into output beyond the explicitly supplied signature
pattern/mask.
"""

import argparse
import json
import sys

import qualify_signature


def build_verified(report, signature_id, name, family, source_reference,
                   provenance_note, verifier, cleaner):
    if not report.get("qualified"):
        raise ValueError("qualification gate did not pass")
    return {
        "schema": 1,
        "id": signature_id,
        "name": name,
        "family": family,
        "kind": "bootblock",
        "status": "verified",
        "synthetic": False,
        "source": {
            "reference": source_reference,
        },
        "provenance": {
            "method": "isolated sample qualification with clean-corpus regression",
            "note": provenance_note,
            "sample_bootblock_sha256": report["sample_bootblock_sha256"],
            "clean_entries_tested": len(report["clean_results"]),
        },
        "sample_sha256": report["sample_bootblock_sha256"],
        "signature": {
            "offset": report["offset"],
            "bytes": report["pattern"],
            "mask": report["mask"],
        },
        "verifier": verifier,
        "cleaner": cleaner,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate an AmiGuard verified-signature metadata draft")
    parser.add_argument("sample", help="isolated local malware sample or disk image")
    parser.add_argument("--clean-manifest", required=True)
    parser.add_argument("--offset", required=True, type=int)
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--mask", required=True)
    parser.add_argument("--id", dest="signature_id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--provenance-note", required=True)
    parser.add_argument("--verifier", default="none")
    parser.add_argument("--cleaner", default="none")
    parser.add_argument("-o", "--output", help="write JSON draft to this path")
    args = parser.parse_args(argv)

    try:
        report = qualify_signature.qualify(
            args.sample, args.clean_manifest, args.offset, args.pattern, args.mask)
        metadata = build_verified(
            report, args.signature_id, args.name, args.family, args.source,
            args.provenance_note, args.verifier, args.cleaner)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("signature promotion: %s" % exc, file=sys.stderr)
        return 1

    rendered = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except OSError as exc:
            print("signature promotion: %s" % exc, file=sys.stderr)
            return 1
        print("Wrote verified metadata draft to %s" % args.output)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
