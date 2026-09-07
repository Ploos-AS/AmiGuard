#!/usr/bin/env python3
"""Review an M2.2m byte-window observation without activating a signature."""

import argparse
import json
import re
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HEX_RE = re.compile(r"^[0-9a-f]+$")


def load_analysis(path):
    data = json.loads(Path(path).read_text())
    if data.get("schema") != 1 or data.get("kind") != "amiguard-research-sample-analysis":
        raise ValueError("invalid M2.2m analysis report")
    if data.get("malware_claim") is not False or data.get("native_activation") is not False:
        raise ValueError("analysis report violates neutral safety contract")
    sample = data.get("sample") or {}
    digest = sample.get("sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ValueError("analysis sample SHA-256 is invalid")
    windows = (data.get("observations") or {}).get("candidate_windows")
    if not isinstance(windows, list):
        raise ValueError("analysis candidate_windows must be a list")
    return data


def find_window(analysis, offset, hex_bytes):
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if not isinstance(hex_bytes, str):
        raise ValueError("hex bytes must be a string")
    hex_bytes = hex_bytes.lower()
    if not HEX_RE.fullmatch(hex_bytes) or len(hex_bytes) % 2:
        raise ValueError("candidate hex must be non-empty even-length lowercase/uppercase hex")
    for item in analysis["observations"]["candidate_windows"]:
        if item.get("offset") == offset and str(item.get("hex", "")).lower() == hex_bytes:
            expected_len = len(hex_bytes) // 2
            if item.get("length") != expected_len:
                raise ValueError("candidate window length is inconsistent")
            return expected_len, hex_bytes
    raise ValueError("candidate must exactly match an M2.2m observed window")


def build_review(analysis, offset, hex_bytes, reviewer, rationale):
    if not reviewer.strip():
        raise ValueError("reviewer is required")
    if not rationale.strip():
        raise ValueError("rationale is required")
    length, normalized = find_window(analysis, offset, hex_bytes)
    return {
        "schema": 1,
        "kind": "amiguard-file-signature-candidate-review",
        "status": "research-candidate",
        "sample": {
            "sha256": analysis["sample"]["sha256"],
            "size": analysis["sample"]["size"],
        },
        "analysis_intake_id": analysis.get("intake_id"),
        "candidate": {
            "offset": offset,
            "length": length,
            "hex": normalized,
            "mask": "ff" * length,
        },
        "review": {
            "reviewer": reviewer.strip(),
            "rationale": rationale.strip(),
            "human_approved_for_further_research": True,
        },
        "requirements": {
            "sample_backed_verification": True,
            "clean_corpus_regression": True,
            "native_runtime_qualification": True,
            "separate_lifecycle_promotion": True,
        },
        "candidate_is_verified_signature": False,
        "malware_claim": False,
        "native_activation": False,
        "promotion": None,
        "cleaner": None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("--offset", required=True, type=int)
    ap.add_argument("--hex", required=True, dest="hex_bytes")
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--rationale", required=True)
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    try:
        analysis = load_analysis(args.analysis)
        report = build_review(
            analysis, args.offset, args.hex_bytes, args.reviewer, args.rationale
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(str(exc))

    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
