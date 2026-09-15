#!/usr/bin/env python3
import argparse
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGNATURE_ROOT = os.path.join(ROOT, "signatures")
DEFAULT_OUTPUT = os.path.join(SIGNATURE_ROOT, "manifest.json")
SCHEMA = 1
DATABASE_VERSION = 1


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def load_records(signature_root=SIGNATURE_ROOT):
    records = []
    pattern = os.path.join(signature_root, "**", "*.json")
    for path in sorted(glob.glob(pattern, recursive=True)):
        if os.path.abspath(path) == os.path.abspath(os.path.join(signature_root, "manifest.json")):
            continue
        with open(path, "r", encoding="utf-8") as handle:
            item = json.load(handle)
        if not isinstance(item, dict):
            raise ValueError("%s: signature metadata must be an object" % path)
        for key in ("id", "kind", "status", "synthetic"):
            if key not in item:
                raise ValueError("%s: missing %s" % (path, key))
        records.append({
            "path": os.path.relpath(path, ROOT).replace(os.sep, "/"),
            "id": item["id"],
            "kind": item["kind"],
            "status": item["status"],
            "synthetic": item["synthetic"],
            "sample_sha256": item.get("sample_sha256"),
        })
    return records


def build_manifest(records):
    inventory = {}
    for record in records:
        key = "%s:%s" % (record["kind"], record["status"])
        inventory[key] = inventory.get(key, 0) + 1

    production = [r for r in records
                  if r["status"] == "verified" and not r["synthetic"]]
    production.sort(key=lambda r: (r["kind"], r["id"], r["path"]))
    identity = hashlib.sha256(canonical_bytes(production)).hexdigest()

    return {
        "schema": SCHEMA,
        "database_version": DATABASE_VERSION,
        "database_identity": "sha256:%s" % identity,
        "production_signature_count": len(production),
        "production_signatures": production,
        "inventory": dict(sorted(inventory.items())),
        "record_count": len(records),
    }


def render(signature_root=SIGNATURE_ROOT):
    return json.dumps(build_manifest(load_records(signature_root)),
                      indent=2, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        rendered = render()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("signature manifest: %s" % exc, file=sys.stderr)
        return 1

    if args.write:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
        return 0

    try:
        with open(args.output, "r", encoding="utf-8") as handle:
            current = handle.read()
    except OSError as exc:
        print("signature manifest: %s" % exc, file=sys.stderr)
        return 1
    if current != rendered:
        print("signature manifest: stale; run tools/build_signature_manifest.py --write", file=sys.stderr)
        return 1
    print("Signature database manifest is deterministic and current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
