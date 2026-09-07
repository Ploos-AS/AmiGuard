# M2.2 — File signature/test framework

## Goal

Establish the host-side metadata and compilation lifecycle for future AmiGuard
file-virus signatures without changing the native file-scan verdicts yet.

M2.2 deliberately mirrors the conservative bootblock signature lifecycle:

`research -> qualified -> verified`

with `test-only` reserved for synthetic project fixtures.

Only `test-only` and `verified` records are rendered into the generated file
signature table. `research` and `qualified` records remain inactive.

## Metadata

File signature records live under:

```
signatures/files/
```

Schema 1 requires:

- id, name, family, kind=`file`
- status: `test-only`, `research`, `qualified`, or `verified`
- synthetic flag
- source and provenance objects
- sample SHA-256 according to lifecycle state
- one masked fixed-offset signature
- verifier and cleaner metadata

The initial compiler limits signatures to the existing M2.1 128 KiB intake
window. A signature may not extend beyond that bound and native pattern length
is limited to 255 bytes.

## Lifecycle rules

### test-only

Synthetic only. No sample hash. A concrete signature is required. This is used
for harmless project qualification fixtures and must never be represented as a
real malware sample.

### research

Non-synthetic candidate only. No claimed sample hash and no production
signature. Research notes may identify candidate material or public references,
but nothing is activated.

### qualified

Non-synthetic, sample-backed candidate with a concrete signature and exact
SHA-256. It is still inactive and must not be rendered into the native table.

### verified

Non-synthetic, sample-backed, explicitly verified signature. Only this state is
eligible for eventual real malware detection.

## Current M2.2 scope

`tools/compile_file_signatures.py` validates metadata and generates
`src/file_signatures_generated.inc`.

The generated table is **not linked into the native scanner in this first M2.2
step**. Therefore M2.2 does not change `AmiGuard FILE` output and does not add
an `INFECTED` verdict yet. Existing M2.1 results remain structural only:
`VALID-HUNK`, `NOT-HUNK`, `MALFORMED-HUNK`, and `ERROR`.

A harmless synthetic marker is included solely to prove the compiler path.

## Research inputs

Zeeball AV-Testfile is a promising harmless positive-test candidate for a later
step, but must first be independently obtained, hashed, and its redistribution
and usage terms recorded. It is not treated as a verified AmiGuard signature by
this milestone.

`VirusZ_III.Bootblocks` is relevant to the known-clean bootblock corpus rather
than file-virus activation. Its format, provenance, and redistribution terms
must be researched separately before import.

xvs.library may be used as a research/reference source only when licensing and
provenance permit. AmiGuard must not depend on it at runtime.

## Qualification

Run:

```
make check
```

Acceptance requires:

- bootblock signature checks still pass;
- file signature generated table is current;
- lifecycle validation tests pass;
- research and qualified records are proven inactive;
- verified/test-only rendering behavior is tested;
- M2.1 native source set and runtime behavior are unchanged.

Because this first M2.2 step adds only host-side metadata/compiler/test files and
an unlinked generated include, no new FS-UAE runtime qualification is required.
A visible KS1.2/512 KiB runtime qualification becomes mandatory when file
signature matching is linked into the native executable.
