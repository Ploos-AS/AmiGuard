# M1.10 — Batch bootblock corpus triage

## Purpose

M1.10 adds a read-only host-side corpus triage tool for scanning many local Amiga disk images or raw bootblocks before any malware-signature claim is made.

The goal is to make large clean/research collections tractable while preserving AmiGuard's conservative semantics.

## Tool

`tools/triage_corpus.py`

Inputs may be individual files and/or directories. Directory traversal is non-recursive by default; `--recursive` enables recursive traversal.

Each file is passed through the same structural analysis implemented by `tools/analyze_bootblock.py`.

Example:

```sh
python3 tools/triage_corpus.py /path/to/corpus --recursive --json > triage.json
```

The tool never modifies input files.

## Report schema

The JSON report uses:

- `schema: 1`
- `kind: amiguard-bootblock-corpus-triage`
- total files seen/analyzed/failed
- number of unique bootblocks
- counts for `STANDARD`, `CUSTOM`, and `UNKNOWN`
- one record per successfully analyzed file
- duplicate groups keyed by exact bootblock SHA-256
- per-file errors for malformed/unreadable inputs
- `malware_claim: false`

Deduplication is based on SHA-256 of the first 1024 bytes only. Two different disk images with the same bootblock therefore belong to the same duplicate bootblock group while retaining their separate whole-input SHA-256 values.

## Safety semantics

M1.10 does not detect malware and must not be interpreted as doing so.

- `STANDARD` means DOS0-DOS7 with a valid bootblock checksum.
- `CUSTOM` means non-DOS with a valid bootblock checksum.
- `UNKNOWN` means structurally unrecognized or checksum-invalid.
- none of these classifications are equivalent to clean or infected.
- every corpus report and every successful record carries `malware_claim: false`.
- only a compiled, verified malware signature in the native scanner may produce `INFECTED`.

A malformed or too-short file is recorded in `errors` and does not invalidate analysis of the rest of the corpus.

## Qualification

M1.10 is host-side only. It changes no native Amiga scanner/runtime code, so visible FS-UAE runtime requalification is not required.

Qualification requires:

- existing C scanner tests PASS
- trackdisk tests PASS
- all Python tests PASS, including corpus counting, exact bootblock deduplication, malformed-file isolation, recursive traversal, and neutral malware semantics
- GitHub Actions CI PASS
