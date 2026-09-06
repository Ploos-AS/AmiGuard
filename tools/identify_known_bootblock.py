#!/usr/bin/env python3
"""Read-only exact SHA-256 identification of known-clean bootblocks."""

import argparse
import hashlib
import json
import os
import sys

BOOTBLOCK_SIZE = 1024
DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          "known-clean", "bootblocks.json")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_bootblock(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) < BOOTBLOCK_SIZE:
        raise ValueError("input is shorter than 1024 bytes")
    return data[:BOOTBLOCK_SIZE]


def load_database(path):
    with open(path, "r", encoding="utf-8") as handle:
        db = json.load(handle)
    if db.get("schema") != 1 or not isinstance(db.get("entries"), list):
        raise ValueError("unsupported known-clean database schema")
    seen_ids = set()
    seen_hashes = set()
    for entry in db["entries"]:
        if not isinstance(entry, dict):
            raise ValueError("known-clean entry must be an object")
        entry_id = entry.get("id")
        digest = entry.get("bootblock_sha256")
        status = entry.get("status")
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError("known-clean entry requires id")
        if entry_id in seen_ids:
            raise ValueError("duplicate known-clean id: %s" % entry_id)
        seen_ids.add(entry_id)
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError("known-clean entry requires 64-hex SHA-256")
        try:
            int(digest, 16)
        except ValueError:
            raise ValueError("known-clean SHA-256 is not hexadecimal")
        digest = digest.lower()
        if digest in seen_hashes:
            raise ValueError("duplicate known-clean SHA-256: %s" % digest)
        seen_hashes.add(digest)
        entry["bootblock_sha256"] = digest
        if status not in ("test-only", "verified-clean"):
            raise ValueError("known-clean status must be test-only or verified-clean")
        if status == "verified-clean" and not entry.get("provenance"):
            raise ValueError("verified-clean entry requires provenance")
    return db


def identify(bootblock, db):
    digest = sha256(bootblock)
    for entry in db["entries"]:
        if entry["bootblock_sha256"] == digest:
            return digest, entry
    return digest, None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Identify a bootblock using exact known-clean SHA-256 fingerprints")
    parser.add_argument("input", help="raw bootblock or disk image")
    parser.add_argument("--database", default=DEFAULT_DB,
                        help="known-clean database JSON")
    parser.add_argument("--json", action="store_true",
                        help="print machine-readable result")
    args = parser.parse_args(argv)

    try:
        bootblock = load_bootblock(args.input)
        db = load_database(args.database)
        digest, entry = identify(bootblock, db)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("known-clean identifier: %s" % exc, file=sys.stderr)
        return 2

    result = {
        "bootblock_sha256": digest,
        "known_clean": entry is not None,
        "match": entry,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif entry is None:
        print("UNLISTED: %s" % digest)
    else:
        print("KNOWN-CLEAN: %s (%s)" % (entry["name"], entry["id"]))
    return 0 if entry is not None else 1


if __name__ == "__main__":
    sys.exit(main())
