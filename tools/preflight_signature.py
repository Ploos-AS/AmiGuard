#!/usr/bin/env python3
"""Side-effect-free preflight for an AmiGuard qualified signature draft.

The draft is validated with the same schema rules as compile_signatures.py and
combined with current repository metadata in memory. Qualified records are not
rendered into the native signature table; this preflight proves that their
metadata and future verified form are compatible without compiling them early.
"""

import argparse
import json
import os
import sys

import compile_signatures


def load_draft(path):
    with open(path, "r", encoding="utf-8") as handle:
        item = json.load(handle)
    compile_signatures.validate(path, item)
    if item["status"] != "qualified":
        raise ValueError("preflight requires status=qualified")
    return item


def preflight(path):
    draft = load_draft(path)
    current = compile_signatures.load_items()

    for item in current:
        if item["id"] == draft["id"]:
            raise ValueError("signature id already exists: %s" % draft["id"])

    combined = current + [draft]
    rendered_without_qualified = compile_signatures.render(combined)
    verified = dict(draft)
    verified["status"] = "verified"
    compile_signatures.validate(path, verified)
    rendered_verified = compile_signatures.render(current + [verified])
    return {
        "draft": os.path.abspath(path),
        "id": draft["id"],
        "status": draft["status"],
        "sample_sha256": draft["sample_sha256"],
        "current_records": len(current),
        "combined_records": len(combined),
        "qualified_compiled": False,
        "native_table_bytes_without_qualified": len(rendered_without_qualified.encode("utf-8")),
        "native_table_bytes_if_verified": len(rendered_verified.encode("utf-8")),
        "preflight_pass": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Side-effect-free AmiGuard qualified-signature preflight")
    parser.add_argument("draft", help="generated qualified metadata JSON draft")
    args = parser.parse_args(argv)

    try:
        report = preflight(args.draft)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("signature preflight: %s" % exc, file=sys.stderr)
        return 1

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
