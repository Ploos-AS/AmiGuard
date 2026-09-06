# M1.4 — Kickstart 1.2 runtime requalification

## Purpose

Requalify the M1.4 custom-bootblock classification change on the minimum supported runtime. The key runtime-visible change is that a non-DOS bootblock with a valid Amiga bootblock checksum is reported as `CUSTOM`, not `UNKNOWN`.

## Required environment

- FS-UAE visible, not headless
- exactly one relevant FS-UAE instance
- existing `a500-stock-accurate` profile
- A500 / Motorola 68000
- Kickstart 1.2 (33.180)
- Workbench 1.2 (33.56)
- 512 KiB Chip RAM
- no Fast/Slow RAM
- native AmiGuard built with Bebbo `m68k-amigaos-gcc -m68000`

Reuse the previously qualified M1.3 environment and safe fixtures where possible. Do not modify original Workbench/reference media. All scanner access must remain read-only.

## Gates

### R1 — Repository/baseline

Record starting HEAD, `origin/main`, divergence, and worktree status. The tree must include the M1.4 classification implementation and this document.

### R2 — Host tests and native build

Run:

```sh
make clean
make check
make
```

Expected:

- all host tests PASS;
- existing checksum carry-wrap regression PASS;
- M1.4 valid non-DOS custom bootblock regression PASS;
- all Python tests PASS;
- native Motorola 68000 build PASS.

Record compiler version and executable size.

### R3 — Visible KS1.2 startup

Start exactly one visible FS-UAE instance with the minimum qualified profile and launch AmiGuard.

Expected: no crash, hang, missing API/library, or OS 2.x dependency.

### R4 — Valid DOS regression

Scan the same known-clean DOS test/Workbench ADF used for M1.3 where available:

```text
AmiGuard DF0:
```

Expected:

```text
trackdisk.device: read 1024 bytes at offset 0
STANDARD: Amiga DOS bootblock (valid checksum)
```

It must not be reported as `CUSTOM`, `UNKNOWN`, or `INFECTED`.

### R5 — Valid custom bootblock => CUSTOM

Use a harmless disposable non-DOS bootblock fixture whose 1024-byte Amiga checksum is valid. Prefer the existing safe custom fixture if it can be made/verified checksum-valid without touching an original image. Otherwise create a disposable local fixture/image solely for this qualification.

Scan it with:

```text
AmiGuard DF0:
```

Expected:

```text
CUSTOM: custom bootblock (valid checksum)
```

It must not be reported as `STANDARD`, `UNKNOWN`, or `INFECTED`.

Record how the fixture was constructed/verified, but do not commit copyrighted disk images.

### R6 — Invalid/unknown regressions

Recheck both safe negative cases:

1. DOS magic retained but checksum invalid =>

```text
UNKNOWN: Amiga DOS bootblock (invalid checksum)
```

2. Non-DOS unrecognized block with invalid checksum =>

```text
UNKNOWN: unknown bootblock
```

Neither case may be reported as `CUSTOM` merely because it is non-DOS.

### R7 — Stability/minimum memory

On the visible A500 / KS1.2 / 512 KiB session, perform at least 10 repeated scans covering the valid DOS and/or valid CUSTOM case.

Expected:

- 10/10 successful 1024-byte reads;
- classifications remain stable;
- no crash/hang;
- no obvious progressive Chip RAM loss.

Record free Chip RAM before/after if practical.

### R8 — Read-only media integrity

For every host-backed ADF used during R4-R6, record SHA-256 before and after runtime testing.

Expected: all hashes unchanged.

## Acceptance

M1.4 runtime requalification is PASS only when R1-R8 are PASS. Any mandatory untested gate is `UNVERIFIED`; do not infer runtime PASS from CI or host tests.

`CUSTOM` is a neutral structural classification. It is not a malware verdict. `INFECTED` remains reserved for compiled signature matches.

## Result record

Fill in after execution:

| Gate | Result | Evidence |
| --- | --- | --- |
| R1 Repository/baseline | UNVERIFIED | |
| R2 Host + native build | UNVERIFIED | |
| R3 Visible KS1.2 startup | UNVERIFIED | |
| R4 Valid DOS => STANDARD | UNVERIFIED | |
| R5 Valid non-DOS checksum => CUSTOM | UNVERIFIED | |
| R6 Invalid/unknown regressions | UNVERIFIED | |
| R7 Stability / 512 KiB | UNVERIFIED | |
| R8 Read-only hashes | UNVERIFIED | |

Also record:

- Starting HEAD
- Final HEAD
- `origin/main`
- divergence
- worktree status
- compiler/toolchain version
- native executable size
- FS-UAE version/profile
- Kickstart/Workbench versions
- CPU and RAM
- exact observed CLI output for STANDARD, CUSTOM, and UNKNOWN cases
- SHA-256 before/after for every test image
- visible FS-UAE instance count
- screenshot/log/evidence paths where applicable
- blockers

Do not tag or create a release as part of this requalification.
