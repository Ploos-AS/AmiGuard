# M1.5 — Known-clean bootblock fingerprints

M1.5 adds a host-side, read-only exact identification layer for known-clean bootblocks.

## Design

- Identification uses the SHA-256 of the first 1024 bytes only.
- A match is exact; there is no fuzzy or heuristic clean classification.
- The known-clean database is separate from malware signatures.
- `KNOWN-CLEAN` is host-side metadata and does not alter the native scanner result.
- `INFECTED` remains reserved for compiled malware-signature matches.
- An unlisted bootblock is reported as `UNLISTED`, never as suspicious or infected.

## Database states

`known-clean/bootblocks.json` schema 1 supports:

- `test-only`: synthetic fixtures used to test the pipeline.
- `verified-clean`: real-world fingerprints accepted only with explicit provenance.

The repository initially contains only a synthetic DOS0 test fixture. No copyrighted bootblock bytes are stored.

## Safety and provenance

A real bootblock must not be added as `verified-clean` merely because it has a DOS identifier or a valid checksum. The exact SHA-256 must be derived from a trusted source and its provenance documented. Multiple independent sources are preferred for operating-system/reference media.

Known-clean status means only that the exact 1024-byte bootblock matches a documented clean reference. It is not a statement about the remaining disk contents.

## Tool

Run:

```sh
python3 tools/identify_known_bootblock.py disk.adf
```

or:

```sh
python3 tools/identify_known_bootblock.py bootblock.bin --json
```

Exit status:

- `0`: exact known-clean match;
- `1`: valid input but fingerprint is unlisted;
- `2`: malformed input/database or I/O error.

## Acceptance

M1.5 host-side foundation is complete when:

1. exact SHA-256 matching is implemented;
2. one-byte changes do not match;
3. malformed/duplicate database entries are rejected;
4. `verified-clean` requires provenance;
5. the tool is part of `make check`;
6. CI passes.

No native Amiga runtime requalification is required for this host-only milestone because no native source or generated runtime table changes.
