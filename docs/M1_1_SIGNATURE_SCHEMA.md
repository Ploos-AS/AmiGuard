# M1.1 — Signature schema and provenance

## Goal

Establish a reproducible signature pipeline before AmiGuard gains real malware detections.

Human-readable metadata lives under `signatures/bootblocks/`. A host-side compiler validates that metadata and emits the compact C table used by the Kickstart 1.2 / Motorola 68000 scanner.

M1.1 deliberately contains synthetic test signatures only. No live malware, third-party signature database, or copied proprietary detection material is added.

## Metadata schema

Each JSON document is one bootblock signature and currently requires:

- `schema`: schema version, currently `1`;
- `id`: stable machine identifier;
- `name`: human-readable detection name;
- `family`: malware family or synthetic fixture family;
- `kind`: currently `bootblock`;
- `status`: `test-only`, `research`, or `verified`;
- `synthetic`: whether the signature was created solely as a safe project fixture;
- `source`: structured source/reference metadata;
- `provenance`: structured authorship/licensing/derivation notes;
- `sample_sha256`: SHA-256 of the analyzed sample for non-synthetic signatures; synthetic fixtures must use `null`;
- `signature.offset`: byte offset inside the 1024-byte bootblock;
- `signature.bytes`: hexadecimal pattern bytes;
- `signature.mask`: hexadecimal bit mask, same length as the pattern;
- `verifier`: additional verifier identifier, currently `none` for fixtures;
- `cleaner`: cleaner identifier, currently `none`.

The compiler rejects duplicate IDs, malformed hex, masks of the wrong length, signatures that extend beyond the 1024-byte bootblock, and non-synthetic entries without a 64-hex-character sample SHA-256.

## Mask semantics

Native matching compares:

`(data_byte & mask_byte) == (pattern_byte & mask_byte)`

A mask byte of `ff` therefore means exact matching. Cleared mask bits are wildcards. M1.1 includes a synthetic masked fixture so this behavior is regression-tested without using malware-derived bytes.

## Generated native table

Run:

```sh
python3 tools/compile_signatures.py --write
```

This deterministically generates `src/signatures_generated.inc`.

CI / host qualification runs:

```sh
python3 tools/compile_signatures.py --check
```

and fails if the checked-in generated table is stale or metadata is invalid.

The native table intentionally contains only the fields required during scanning: detection name, offset, length, pattern, and mask. Provenance, sample hashes, source references, status, verifier planning, and cleaner planning stay host-side so the Amiga binary is not burdened with research metadata.

## Provenance policy for future real signatures

Before a real signature may become `verified`:

1. its analyzed sample must have a recorded SHA-256 outside/publicly without committing the sample itself;
2. the source and legal/provenance basis for deriving the signature must be recorded;
3. the signature must not be copied from a proprietary third-party signature database without permission;
4. public repo fixtures must remain synthetic, redacted, or otherwise non-malicious;
5. detection must be validated against the isolated sample and against clean regression media;
6. cleaner support remains independent and must not be implied by a detection signature.

Research based on public virus descriptions may guide what to inspect, but AmiGuard should derive and document its own detection evidence from legally analyzable material.

## M1.1 acceptance criteria

- host metadata is machine-validated;
- generated native table is deterministic and checked for staleness;
- existing synthetic exact detection still works;
- masked matching is implemented and tested;
- significant masked mismatches are rejected;
- native code remains C89-compatible and 68000-oriented;
- no new AmigaOS runtime dependency is introduced;
- no real malware sample is committed;
- no real malware signature is claimed by this milestone.

M1.2 will use this pipeline for the first provenance-backed historical bootblock-virus detections.
