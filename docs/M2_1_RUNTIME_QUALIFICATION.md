# M2.1 — Kickstart 1.2 runtime qualification

## Result: PENDING

M2.1 introduces native read-only file intake through `AmiGuard FILE <path>` and
therefore requires visible native qualification before the milestone is complete.

## Required environment

Use the established reference runtime:

- visible FS-UAE; never headless
- existing `a500-stock-accurate` profile
- A500 / Motorola 68000
- Kickstart 1.2 / 33.180
- Workbench 1.2 / 33.56
- 512 KiB Chip RAM
- no Fast/Slow/motherboard RAM
- one visible emulator instance only

Do not modify the reference profile permanently. Disposable overlays and harmless
fixtures are allowed. No malware sample is required for M2.1.

## R1 — repository and build

Record starting HEAD, tested HEAD, origin/main, divergence and worktree state.
Run `make clean`, `make check`, and the native Bebbo build. Record compiler
version, `-m68000 -mcrt=nix13`, binary format/architecture, executable size and
SHA-256. All C tests, HUNK tests, file-intake tests and Python tests must PASS.

## R2 — native startup on minimum target

Run the qualified AmiGuard binary in one visible FS-UAE instance on the target
above. Verify normal startup with no crash, hang, missing API/library or OS 2.x
dependency.

## R3 — VALID-HUNK file path

Create or reuse a harmless small HUNK fixture accepted by the M2.0 parser. Run:

```
AmiGuard FILE <path>
```

Expected neutral classification:

```
VALID-HUNK
```

This means structural validity within AmiGuard's supported HUNK subset only; it
is not a clean or malware verdict.

## R4 — NOT-HUNK file path

Use a harmless non-HUNK file. Expected classification:

```
NOT-HUNK
```

## R5 — MALFORMED-HUNK file path

Use a harmless file beginning as HUNK but intentionally structurally truncated
or invalid. Expected classification:

```
MALFORMED-HUNK
```

## R6 — bounded-input error path

Exercise at least one controlled file-intake error. Prefer the documented
oversize boundary (>128 KiB) if practical; otherwise exercise an unreadable or
missing path. It must report `ERROR`/controlled failure and must not be presented
as a HUNK or malware classification.

## R7 — file stability and 512 KiB behavior

Repeat at minimum:

- VALID-HUNK: 10/10
- NOT-HUNK: 5/5
- MALFORMED-HUNK: 5/5

All classifications must remain stable with no crash, hang, progressive memory
loss or resource leak. Record free Chip RAM before/after if the established
harness supports it.

## R8 — read-only file integrity

Hash every runtime file fixture before and after all scans. All SHA-256 values
must be identical. Verify source inspection shows no write/rename/delete/
quarantine path in M2.1 file intake.

## R9 — bootblock regression

The existing floppy path must remain unchanged. At minimum re-run one known
STANDARD bootblock and one known CUSTOM bootblock and confirm the expected M1.4
classifications. No file-mode parsing may interfere with `DF0:`–`DF3:` parsing.

## R10 — semantic safety

Confirm runtime output and source behavior preserve these rules:

- VALID-HUNK = structural parser acceptance only.
- NOT-HUNK = no HUNK header.
- MALFORMED-HUNK = HUNK-like input failing structural validation.
- ERROR = intake/resource/path failure.
- None means infected, suspicious, or clean.
- No signature match, heuristic malware verdict, cleaning, quarantine, rename,
  delete or file write is introduced by M2.1.

## Completion gate

M2.1 is complete only when R1–R10 PASS, evidence/documentation is committed and
pushed, and GitHub CI passes on the exact final qualified HEAD. If any gate
fails, leave this document as FAIL/PENDING, diagnose the cause, and re-run all
relevant gates after a code fix.
