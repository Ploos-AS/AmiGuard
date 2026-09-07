# M2.2b — Native file signature matcher runtime qualification

Status: PENDING

## Scope

M2.2b links the generated file-signature table and native masked matcher into
`AmiGuard FILE <path>`.

The only active file signature at this milestone is the synthetic
`test-only` AmiGuard marker. It must report `TEST-SIGNATURE`, never
`INFECTED`. Future `verified` non-synthetic file signatures may report
`INFECTED`; `research` and `qualified` records remain absent from the native
table.

This milestone changes native code and therefore requires visible AmigaOS 1.2
runtime qualification before completion.

## Baseline

Implementation HEAD before this qualification gate:

`0bf219057b5d6229d8a546630c4f54300a54d5c8`

GitHub CI #144 / run 34089994161: PASS on that exact HEAD.

## Required environment

- one visible FS-UAE instance; never headless
- established `a500-stock-accurate` profile
- Amiga 500 / Motorola 68000
- Kickstart 1.2 / 33.180
- Workbench 1.2 / 33.56
- 512 KiB Chip RAM only
- no Fast/Slow/extra motherboard RAM
- native Bebbo build with `-m68000 -mcrt=nix13`

## Gates

### R1 — repository/build baseline

Record starting/tested/final HEAD, origin/main, divergence and worktree state.
Run `make clean`, `make check`, and native `make`. Record compiler version,
binary size, SHA-256 and 68000/loadseg evidence.

### R2 — native matcher linkage

Confirm `src/file_signatures.c` is linked into AmiGuard and
`src/file_signatures_generated.inc` is current. Host matcher tests must PASS.

### R3 — synthetic positive test

Create a harmless file containing the exact synthetic marker
`AMIGUARD-FILE-TEST` at byte offset 4. Run:

```
AmiGuard FILE <fixture>
```

Expected result begins:

```
TEST-SIGNATURE: AmiGuard synthetic file test marker
```

It must not say `INFECTED`.

### R4 — near-miss negative test

Change at least one byte inside the synthetic marker while preserving file
size. The file must not match `TEST-SIGNATURE`. Its ordinary HUNK/non-HUNK
classification must remain deterministic.

### R5 — M2.1 file classification regression

Re-run harmless fixtures for:

- `VALID-HUNK`
- `NOT-HUNK`
- `MALFORMED-HUNK`
- oversize controlled `ERROR`
- missing-file controlled `ERROR`

All M2.1 semantics must remain unchanged when no signature matches.

### R6 — match precedence

Construct a harmless file whose content would otherwise classify as
NOT-HUNK, but which contains the synthetic marker at offset 4. It must report
`TEST-SIGNATURE`, proving signature matching occurs before structural fallback.

Do not use real malware.

### R7 — 512 KiB stability

On the same visible 512 KiB system run at least:

- synthetic positive: 10/10
- near-miss: 10/10
- one ordinary M2.1 class: 10/10

No crash, hang, Guru Meditation or progressive memory loss. Record free Chip
RAM before/after if practical.

### R8 — read-only integrity

Hash every runtime fixture before and after. All hashes must be identical.
Confirm no file write/create/truncate/rename/clean/quarantine path was added.

### R9 — bootblock regression

Verify existing `AmiGuard DF0:` behavior remains intact with at least one
STANDARD fixture and, if available, the established harmless CUSTOM fixture.

### R10 — lifecycle safety

Prove from metadata/compiler/generated table that:

- `test-only` is native but explicitly marked test-only;
- the synthetic test signature produces `TEST-SIGNATURE`, not `INFECTED`;
- `research` is not rendered;
- `qualified` is not rendered;
- only future `verified` non-synthetic records can produce file `INFECTED`.

## Completion

All R1-R10 must PASS on one qualified HEAD. Update this document with exact
observations/evidence, commit directly to `main`, push, and require final
GitHub CI `completed/success` on the exact final HEAD.

Do not mark M2.2b complete on host/CI evidence alone.
