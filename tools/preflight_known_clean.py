#!/usr/bin/env python3
"""Preflight candidate-clean -> verified-clean promotion without side effects."""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
DEFAULT_DB = os.path.join(ROOT, "known-clean", "bootblocks.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def valid_sha256(value):
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def validate_candidate(entry):
    required_text = ("id", "name", "source", "provenance")
    for key in required_text:
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            raise ValueError("candidate-clean requires %s" % key)
    if entry.get("status") != "candidate-clean":
        raise ValueError("entry status must be candidate-clean")
    if not valid_sha256(entry.get("bootblock_sha256")):
        raise ValueError("candidate-clean requires 64-hex bootblock_sha256")
    input_meta = entry.get("input")
    if not isinstance(input_meta, dict):
        raise ValueError("candidate-clean requires input metadata")
    if not valid_sha256(input_meta.get("sha256")):
        raise ValueError("candidate-clean input requires 64-hex sha256")
    if not isinstance(input_meta.get("size"), int) or input_meta["size"] < 1024:
        raise ValueError("candidate-clean input requires size >= 1024")


def validate_review(review, entry):
    if not isinstance(review, dict) or review.get("schema") != 1:
        raise ValueError("review schema must be 1")
    if review.get("candidate_id") != entry["id"]:
        raise ValueError("review candidate_id does not match entry id")
    if review.get("bootblock_sha256") != entry["bootblock_sha256"]:
        raise ValueError("review bootblock_sha256 does not match candidate")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        raise ValueError("review requires reviewer")
    if not isinstance(review.get("method"), str) or not review["method"].strip():
        raise ValueError("review requires method")
    if not isinstance(review.get("evidence"), str) or not review["evidence"].strip():
        raise ValueError("review requires evidence")
    if review.get("decision") != "verified-clean":
        raise ValueError("review decision must be verified-clean")


def check_database(db, entry):
    if db.get("schema") != 1 or not isinstance(db.get("entries"), list):
        raise ValueError("unsupported known-clean database schema")
    for existing in db["entries"]:
        if existing.get("id") == entry["id"]:
            raise ValueError("candidate id already exists in database")
        if existing.get("bootblock_sha256", "").lower() == entry["bootblock_sha256"].lower():
            raise ValueError("candidate SHA-256 already exists in database")


def promoted_entry(entry, review):
    result = dict(entry)
    result["status"] = "verified-clean"
    result["verification"] = {
        "reviewer": review["reviewer"],
        "method": review["method"],
        "evidence": review["evidence"],
    }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Preflight AmiGuard candidate-clean promotion")
    parser.add_argument("candidate", help="candidate-clean JSON entry")
    parser.add_argument("review", help="independent review JSON")
    parser.add_argument("--database", default=DEFAULT_DB)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        entry = load_json(args.candidate)
        review = load_json(args.review)
        db = load_json(args.database)
        validate_candidate(entry)
        validate_review(review, entry)
        check_database(db, entry)
        promoted = promoted_entry(entry, review)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("known-clean preflight: %s" % exc, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(promoted, indent=2, sort_keys=True))
    else:
        print("PREFLIGHT PASS: %s -> verified-clean" % entry["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
