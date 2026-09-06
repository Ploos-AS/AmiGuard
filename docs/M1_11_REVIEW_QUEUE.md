# M1.11 — Neutral corpus review queue

M1.11 adds a host-side, read-only review queue builder for AmiGuard bootblock corpus triage results.

## Purpose

`tools/build_review_queue.py` consumes JSON produced by `tools/triage_corpus.py` and groups unique non-standard bootblocks for manual review.

The queue is triage convenience only. It is not a malware detector and never makes a malware claim.

## Selection and ordering

- `STANDARD` records are excluded from the manual review queue.
- `CUSTOM` and `UNKNOWN` records are grouped by exact bootblock SHA-256.
- Identical bootblocks are collapsed into one item with occurrence count and source paths.
- Printable strings from duplicate records are merged without duplication.
- Current review ordering places `CUSTOM` before `UNKNOWN`, then higher occurrence counts first, then SHA-256 for deterministic ordering.

This ordering is deliberately operational rather than evidentiary. A high-ranked item is not more likely to be malware merely because of its queue position.

## Safety semantics

Every queue and queue item contains `malware_claim: false`.

`CUSTOM` means a non-DOS bootblock with a valid Amiga bootblock checksum. `UNKNOWN` means the structural classification is not recognized as a checksum-valid standard/custom bootblock. Neither classification means infected.

Only a separate verified AmiGuard malware signature may produce an `INFECTED` verdict.

## Validation

The builder rejects malformed triage reports, invalid classifications, invalid bootblock hashes, and inconsistent duplicate records.

Unit tests cover:

- exclusion of STANDARD records;
- unique CUSTOM/UNKNOWN queue generation;
- duplicate collapse and occurrence counting;
- string merging;
- neutral malware semantics;
- rejection of inconsistent or malformed input.

`make check` includes the M1.11 tests.

## Runtime impact

M1.11 changes host-side research tooling only. No native Amiga source, scanner result, generated signature table, or trackdisk behavior is changed, so no visible FS-UAE runtime requalification is required.
