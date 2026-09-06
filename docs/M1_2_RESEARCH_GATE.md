# M1.2 — Research-to-verified gate

## Goal

Introduce the first real historical bootblock-virus research records without allowing unverified material into AmiGuard's native detection table.

M1.2 separates three states:

- `test-only`: synthetic regression fixtures; compiled into the native table.
- `research`: documented candidate families/markers; never compiled into the native table.
- `verified`: non-synthetic detections backed by a recorded sample SHA-256, stable signature evidence, clean-media regression checks, and isolated sample validation; compiled into the native table.

No live malware is committed to this repository.

## First research candidate

The first candidate is the historical Mount / Eleni 2.2 bootblock virus documented by Virus Help Team. The public description identifies it as a 1024-byte bootblock/file virus and documents an invariant encoded text marker near the top of the bootblock. The research record preserves only the candidate metadata needed to guide isolated verification; it is not a claimed detection signature yet.

Before promotion to `verified`, AmiGuard requires:

1. a legally analyzable isolated sample;
2. SHA-256 of the analyzed bootblock/sample;
3. independently measured exact offset and bytes from that sample;
4. confirmation that the candidate marker is stable across available variants;
5. negative regression against clean Workbench and known custom bootblocks;
6. runtime detection validation on the Kickstart 1.2 scanner;
7. provenance notes documenting how the signature was derived.

## Safety rule

A public encyclopedia description is research evidence, not sufficient proof for a production signature. Research entries must therefore be excluded from `src/signatures_generated.inc` until promoted to `verified`.

## M1.2a acceptance criteria

- metadata compiler accepts incomplete non-synthetic `research` entries with no sample hash/signature;
- research entries are validated but excluded from native generated output;
- non-synthetic `verified` entries still require a 64-hex SHA-256 and concrete signature;
- `test-only` synthetic fixtures continue to compile and pass existing tests;
- generated table remains deterministic;
- no new runtime dependency is introduced;
- no malware bytes or sample are committed.

## Handoff to M1.2b

M1.2b is sample qualification. Use an isolated local/RAB sample set, never a public repo fixture. Record hashes and derived metadata, then promote only signatures that pass both positive sample detection and negative clean-media regression.
