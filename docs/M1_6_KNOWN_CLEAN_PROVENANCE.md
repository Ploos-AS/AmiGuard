# M1.6 — Known-clean provenance and import lifecycle

## Purpose

M1.6 adds a conservative host-side import path for exact known-clean bootblock fingerprints without weakening AmiGuard's malware semantics.

The native Amiga scanner is unchanged.

## Lifecycle

Known-clean fingerprints have three states:

- `test-only`: synthetic fixtures used by AmiGuard tests.
- `candidate-clean`: exact SHA-256 plus explicit source and provenance are recorded, but the entry is not yet trusted as known-clean.
- `verified-clean`: candidate evidence plus independent clean verification is recorded.

Only `test-only` and `verified-clean` matches are reported as `KNOWN-CLEAN`. A `candidate-clean` match is reported as `CANDIDATE-CLEAN` and `known_clean` remains false in JSON output.

## Import tool

`tools/import_known_clean.py` reads a local raw bootblock or disk image without modifying it. It hashes:

- the complete input image;
- exactly the first 1024 bootblock bytes.

It records DOS type, Amiga bootblock checksum validity, source reference, provenance and optional verification evidence.

The tool prints one JSON entry to stdout and never edits `known-clean/bootblocks.json` automatically. Human review remains required before database insertion.

Example candidate import:

```sh
python3 tools/import_known_clean.py clean.adf \
  --id commodore.example \
  --name "Example known-clean bootblock" \
  --source "owned original media; catalog reference ..." \
  --provenance "read from write-protected original; image SHA-256 ..." \
  > candidate.json
```

Promotion to `verified-clean` additionally requires `--verifier` with independent evidence, for example an independently sourced matching image/hash or another documented clean verification route.

## Safety rules

- Exact SHA-256 fingerprints only.
- No fuzzy or truncated known-clean fingerprint in this milestone.
- A checksum-valid bootblock is not automatically clean.
- `candidate-clean` is not equivalent to trusted clean.
- No copyrighted disk/image bytes are committed by the importer.
- No database mutation happens automatically.
- `INFECTED` remains reserved for compiled malware signature matches in the native scanner.

## Tests

M1.6 tests cover:

- candidate entry generation;
- exact 1024-byte bootblock hashing from larger images;
- DOS/checksum metadata;
- verified-clean rejection without verifier evidence;
- verified-clean generation with verifier evidence;
- short-input rejection.

`make check` includes these tests.

## Runtime impact

None. M1.6 is host-side tooling and metadata validation only, so no Kickstart 1.2 runtime requalification is required unless native code changes later.
