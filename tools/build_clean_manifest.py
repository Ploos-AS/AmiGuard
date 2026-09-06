#!/usr/bin/env python3
"""Build a local clean-media manifest for AmiGuard qualification.

The manifest stores paths and SHA-256 hashes for known-clean disk images or
raw bootblocks. Inputs are read-only and remain outside the repository unless
the user explicitly chooses otherwise.
"""

import argparse
import hashlib
import json
import os
import sys

BOOTBLOCK_SIZE = 1024


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def inspect(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) < BOOTBLOCK_SIZE:
        raise ValueError("%s is shorter than 1024 bytes" % path)
    bootblock = raw[:BOOTBLOCK_SIZE]
    return {
        "path": os.path.abspath(path),
        "input_size": len(raw),
        "input_sha256": sha256(raw),
        "bootblock_sha256": sha256(bootblock),
    }


def build(paths):
    entries = [inspect(path) for path in paths]
    return {
        "schema": 1,
        "kind": "amiguard-clean-bootblock-corpus",
        "entries": entries,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build AmiGuard clean-media manifest")
    parser.add_argument("inputs", nargs="+", help="known-clean ADF/disk images or raw bootblocks")
    parser.add_argument("-o", "--output", required=True, help="manifest JSON path")
    args = parser.parse_args(argv)

    try:
        manifest = build(args.inputs)
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except (OSError, ValueError) as exc:
        print("clean manifest: %s" % exc, file=sys.stderr)
        return 1
    print("Wrote %d clean corpus entries to %s" % (len(manifest["entries"]), args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
