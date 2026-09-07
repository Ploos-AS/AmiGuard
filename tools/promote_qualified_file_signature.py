#!/usr/bin/env python3
"""Create a non-activating qualified file-signature proposal from M2.2n/M2.2o evidence."""

import argparse
import json
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HEX_RE = re.compile(r"^[0-9a-f]+$")


def load_json(path):
    return json.loads(Path(path).read_text())


def parse_review(path):
    review = load_json(path)
    if review.get("schema") != 1 or review.get("kind") != "amiguard-file-signature-candidate-review":
        raise ValueError("invalid M2.2n candidate review")
    if review.get("status") != "research-candidate":
        raise ValueError("candidate review must have status research-candidate")
    if review.get("candidate_is_verified_signature") is not False:
        raise ValueError("candidate review violates unverified contract")
    if review.get("malware_claim") is not False or review.get("native_activation") is not False:
        raise ValueError("candidate review violates neutral safety contract")
    sample = review.get("sample") or {}
    digest = sample.get("sha256")
    size = sample.get("size")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ValueError("candidate sample SHA-256 is invalid")
    if not isinstance(size, int) or size < 0:
        raise ValueError("candidate sample size is invalid")
    candidate = review.get("candidate") or {}
    offset = candidate.get("offset")
    length = candidate.get("length")
    pattern = candidate.get("hex")
    mask = candidate.get("mask")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("candidate offset is invalid")
    if not isinstance(length, int) or length <= 0:
        raise ValueError("candidate length is invalid")
    if not isinstance(pattern, str) or not HEX_RE.fullmatch(pattern) or len(pattern) != length * 2:
        raise ValueError("candidate bytes are invalid")
    if not isinstance(mask, str) or not HEX_RE.fullmatch(mask) or len(mask) != length * 2:
        raise ValueError("candidate mask is invalid")
    if review.get("review", {}).get("human_approved_for_further_research") is not True:
        raise ValueError("candidate lacks explicit human review approval")
    return review


def parse_qualification(path, review):
    qual = load_json(path)
    if qual.get("schema") != 1 or qual.get("kind") != "amiguard-file-signature-candidate-qualification":
        raise ValueError("invalid M2.2o qualification report")
    if qual.get("candidate_status") != "research-candidate":
        raise ValueError("qualification candidate status is invalid")
    if qual.get("differential_qualification_pass") is not True:
        raise ValueError("differential qualification did not pass")
    if qual.get("positive_match") is not True or qual.get("clean_regression_pass") is not True:
        raise ValueError("qualification evidence is incomplete")
    if not isinstance(qual.get("clean_files_tested"), int) or qual["clean_files_tested"] <= 0:
        raise ValueError("qualification must test at least one clean file")
    if qual.get("clean_collisions") != []:
        raise ValueError("qualification contains clean-corpus collisions")
    if qual.get("sample_sha256") != review["sample"]["sha256"]:
        raise ValueError("qualification sample SHA-256 does not match review")
    if qual.get("sample_size") != review["sample"]["size"]:
        raise ValueError("qualification sample size does not match review")
    if qual.get("candidate_is_verified_signature") is not False:
        raise ValueError("qualification violates unverified contract")
    if qual.get("promotion_ready") is not False:
        raise ValueError("M2.2o report must not itself claim promotion readiness")
    if qual.get("malware_claim") is not False or qual.get("native_activation") is not False:
        raise ValueError("qualification violates neutral safety contract")
    return qual


def proposal(review, qual, signature_id, name, family, source, provenance, verifier):
    if not ID_RE.fullmatch(signature_id):
        raise ValueError("invalid signature id")
    for label, value in (("name", name), ("family", family), ("source", source),
                         ("provenance", provenance), ("verifier", verifier)):
        if not value.strip():
            raise ValueError("%s is required" % label)
    candidate = review["candidate"]
    return {
        "schema": 1,
        "id": signature_id,
        "name": name.strip(),
        "family": family.strip(),
        "kind": "file",
        "status": "qualified",
        "synthetic": False,
        "source": {"description": source.strip()},
        "provenance": {
            "description": provenance.strip(),
            "reviewer": review["review"]["reviewer"],
            "review_rationale": review["review"]["rationale"],
            "clean_files_tested": qual["clean_files_tested"],
        },
        "sample_sha256": review["sample"]["sha256"],
        "signature": {
            "offset": candidate["offset"],
            "bytes": candidate["hex"].lower(),
            "mask": candidate["mask"].lower(),
        },
        "verifier": verifier.strip(),
        "cleaner": "none",
        "qualification": {
            "differential_qualification_pass": True,
            "clean_regression_pass": True,
            "clean_files_tested": qual["clean_files_tested"],
        },
        "candidate_is_verified_signature": False,
        "malware_claim": False,
        "native_activation": False,
        "requires_visible_native_runtime": True,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Create an AmiGuard qualified file-signature proposal")
    ap.add_argument("review")
    ap.add_argument("qualification")
    ap.add_argument("--id", required=True, dest="signature_id")
    ap.add_argument("--name", required=True)
    ap.add_argument("--family", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--provenance", required=True)
    ap.add_argument("--verifier", required=True)
    ap.add_argument("-o", "--output")
    args = ap.parse_args(argv)
    try:
        review = parse_review(args.review)
        qual = parse_qualification(args.qualification, review)
        out = proposal(review, qual, args.signature_id, args.name, args.family,
                       args.source, args.provenance, args.verifier)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("qualified proposal: %s" % exc, file=sys.stderr)
        return 2
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
