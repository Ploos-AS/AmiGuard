#!/usr/bin/env python3
"""Create a neutral, non-activating analysis report for an AmiGuard research sample."""

import argparse
import hashlib
import json
import string
from pathlib import Path

MAX_SIZE = 128 * 1024
PRINTABLE = set(bytes(string.printable, "ascii")) - {9, 10, 11, 12, 13}
HUNK_NAMES = {
    0x3E7: "HUNK_UNIT", 0x3E8: "HUNK_NAME", 0x3E9: "HUNK_CODE",
    0x3EA: "HUNK_DATA", 0x3EB: "HUNK_BSS", 0x3EC: "HUNK_RELOC32",
    0x3F0: "HUNK_SYMBOL", 0x3F1: "HUNK_DEBUG", 0x3F2: "HUNK_END",
    0x3F3: "HUNK_HEADER",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def strings(data, minimum=4):
    out = []
    start = None
    for i, b in enumerate(data + b"\x00"):
        if b in PRINTABLE:
            if start is None:
                start = i
        elif start is not None:
            if i - start >= minimum:
                out.append({"offset": start, "text": data[start:i].decode("ascii")})
            start = None
    return out


def hunk_words(data):
    found = []
    for off in range(0, len(data) - 3, 4):
        word = int.from_bytes(data[off:off + 4], "big") & 0x3FFFFFFF
        if word in HUNK_NAMES:
            found.append({"offset": off, "record": HUNK_NAMES[word], "value": word})
    return found


def candidate_windows(data, width=16, limit=16):
    """Neutral candidate windows for human review; never signatures."""
    out = []
    if len(data) < width:
        return out
    seen = set()
    for off in range(0, len(data) - width + 1, max(1, width)):
        chunk = data[off:off + width]
        if len(set(chunk)) < 5 or chunk.count(0) > width // 2:
            continue
        hx = chunk.hex()
        if hx in seen:
            continue
        seen.add(hx)
        out.append({"offset": off, "length": width, "hex": hx})
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sample")
    ap.add_argument("--intake", help="M2.2l intake metadata JSON")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    p = Path(args.sample)
    if p.is_symlink() or not p.is_file():
        raise SystemExit("sample must be a regular non-symlink file")
    data = p.read_bytes()
    if len(data) > MAX_SIZE:
        raise SystemExit("sample exceeds AmiGuard 128 KiB file intake limit")
    digest = sha256(data)

    intake_id = None
    if args.intake:
        intake = json.loads(Path(args.intake).read_text())
        if intake.get("kind") != "amiguard-research-sample-intake":
            raise SystemExit("invalid research intake kind")
        recorded = intake.get("sample", {}).get("sha256")
        if recorded != digest:
            raise SystemExit("sample SHA-256 does not match intake metadata")
        intake_id = intake.get("id")

    report = {
        "schema": 1,
        "kind": "amiguard-research-sample-analysis",
        "sample": {"sha256": digest, "size": len(data)},
        "intake_id": intake_id,
        "observations": {
            "first_u32_be": int.from_bytes(data[:4], "big") if len(data) >= 4 else None,
            "hunk_record_candidates": hunk_words(data),
            "printable_strings": strings(data),
            "candidate_windows": candidate_windows(data),
        },
        "interpretation": {
            "classification": "UNDETERMINED",
            "candidate_windows_are_signatures": False,
            "requires_human_review": True,
            "requires_sample_backed_verification": True,
        },
        "malware_claim": False,
        "native_activation": False,
        "promotion": None,
        "cleaner": None,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
