#!/usr/bin/env python3
"""Side-effect-free preflight for an AmiGuard signature metadata draft.

The draft is validated with the same schema rules as compile_signatures.py and
combined with the current repository metadata in memory. Nothing is written to
signatures/ or src/signatures_generated.inc.
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
    if item["status"] != "verified":
        raise ValueError("preflight requires status=verified")
    return item


def preflight(path):
    draft = load_draft(path)
    current = compile_signatures.load_items()

    for item in current:
        if item["id"] == draft["id"]:
            raise ValueError("signature id already exists: %s" % draft["id"])

    combined = current + [draft]
    rendered = compile_signatures.render(combined)
    return {
        "draft": os.path.abspath(path),
        "id": draft["id"],
        "status": draft["status"],
        "sample_sha256": draft["sample_sha256"],
        "current_records": len(current),
        "combined_records": len(combined),
        "native_table_bytes": len(rendered.encode("utf-8")),
        "preflight_pass": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Side-effect-free AmiGuard verified-signature preflight")
    parser.add_argument("draft", help="generated verified metadata JSON draft")
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
