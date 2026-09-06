# M2.0 — Kickstart 1.2 runtime requalification

## Result: PENDING

M2.0 adds the native HUNK parser (`src/hunk.c`, `src/hunk.h`) to the AmiGuard
binary. Host CI is green, but M2.0 is not complete until the resulting native
68000 executable has been visibly requalified on the established minimum
runtime target.

## Tested code baseline

- Required code HEAD before runtime evidence: `5470e0f26343ec390fd749ceaef61a595448cffc` (`main`).
- GitHub Actions CI #119: PASS.
- The non-HUNK fixture regression was test-only; parser logic was unchanged by
  the CI fix.
- No live malware is required for this qualification.

## Required environment

Use the same established minimum target as M1.4:

- FS-UAE 3.2.35 or the currently installed equivalent.
- Existing `a500-stock-accurate` reference profile, unchanged.
- Amiga 500 / Motorola 68000.
- Kickstart 1.2 / 33.180.
- Workbench 1.2 / 33.56.
- 512 KiB Chip RAM only.
- Visible emulator window; no headless execution.

## Gates

| Gate | Requirement | Status |
| --- | --- | --- |
| R1 | Clean repository; HEAD and origin/main recorded | PENDING |
| R2 | `make clean`, `make check`, native `make` with Bebbo GCC PASS | PENDING |
| R3 | Native binary is Motorola 68000 / Amiga loadseg and size/hash recorded | PENDING |
| R4 | Visible FS-UAE boots A500/KS1.2/512 KiB and AmiGuard starts normally | PENDING |
| R5 | Existing valid DOS bootblock scan still returns STANDARD | PENDING |
| R6 | Existing valid custom bootblock scan still returns CUSTOM | PENDING |
| R7 | Existing invalid DOS/non-DOS scans still return UNKNOWN; no regression to INFECTED/ERROR | PENDING |
| R8 | Repeated scans complete without crash, hang or progressive memory loss | PENDING |
| R9 | All scanned media remain byte-identical before/after; trackdisk path remains read-only | PENDING |

## M2.0-specific acceptance

The HUNK parser is linked into the binary but is not yet exposed as a user-facing
file scanner in M2.0. Therefore this runtime gate is intentionally a regression
qualification of the native executable and existing bootblock path. It proves
that adding the C89 HUNK parser did not introduce an OS 2.x dependency, CPU
requirement above 68000, startup regression, memory regression, or link/runtime
failure on the minimum supported machine.

Host-side parser behavior remains covered by `tests/test_hunk.c`:

- input shorter than four bytes -> NOT-HUNK;
- non-HUNK magic -> NOT-HUNK;
- structurally valid minimal HUNK executable -> VALID-HUNK;
- truncated/unsupported/trailing malformed structure -> MALFORMED.

These parser classifications are structural only. VALID-HUNK does not mean
malware-free, MALFORMED does not mean infected, and no M2.0 parser result may
produce a malware claim.

## Completion rule

Replace `PENDING` with PASS only after all R1-R9 gates have visible/native
evidence. Record compiler version, executable size and SHA-256, FS-UAE/profile
facts, representative CLI output, stability observations, media hashes and any
blockers. Do not call M2.0 complete before this record is updated with the
runtime result.
