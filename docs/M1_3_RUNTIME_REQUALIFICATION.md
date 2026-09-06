# M1.3 — Kickstart 1.2 runtime requalification

## Purpose

Requalify the M1.3 checksum portability fix and the CLI classification wording change on the minimum supported runtime.

## Required environment

- visible FS-UAE, not headless
- A500
- Motorola 68000
- Kickstart 1.2 / Workbench 1.2
- 512 KiB Chip RAM
- native AmiGuard built with `m68k-amigaos-gcc -m68000 -mcrt=nix13`
- reuse the previously qualified `a500-stock-accurate` profile and safe test media where possible

Do not modify reference ROMs, Workbench media, or emulator profiles permanently.

## Gates

### R1 — Baseline build

```sh
make clean
make check
make
```

Expected:

- signature metadata check PASS
- all host tests PASS
- checksum carry-wrap regression PASS
- native 68000 build PASS

Record compiler version and AmiGuard executable size.

### R2 — Valid DOS bootblock → STANDARD

Boot the visible A500/Kickstart 1.2 environment with the same known-clean Workbench/test ADF previously qualified for M1.0.

Run:

```text
AmiGuard DF0:
```

Expected:

- `trackdisk.device` read succeeds
- exactly 1024 bytes are read from offset 0
- output is `STANDARD: Amiga DOS bootblock (valid checksum)`
- output must not use the old `KNOWN:` label
- no crash or hang

### R3 — Invalid-checksum DOS bootblock → UNKNOWN

Reuse a disposable harmless copy of the known-clean image with the DOS magic intact and one non-header bootblock byte changed.

Expected:

- `UNKNOWN: Amiga DOS bootblock (invalid checksum)`
- not `STANDARD`
- not `INFECTED`
- not `ERROR`
- no write or repair action

### R4 — Unknown/custom bootblock regression

Reuse the harmless custom/unknown fixture from earlier qualification.

Expected:

- `UNKNOWN: unknown bootblock`
- no crash or hang
- no media modification

### R5 — Read-only regression

For every host-backed ADF used in R2-R4, record SHA-256 before and after runtime scanning.

Expected: every image hash is unchanged.

### R6 — Minimum runtime

Confirm the tested emulator is actually:

- A500
- 68000
- Kickstart 1.2
- Workbench 1.2
- 512 KiB Chip RAM

Expected: AmiGuard starts, reads DF0:, classifies successfully, and exits normally without missing API/library errors.

### R7 — Repeatability

Repeat the valid DOS scan 10 times in the same visible session.

Expected:

- 10/10 scans return `STANDARD`
- no crash/hang
- no progressive memory/resource failure visible

## Acceptance

M1.3 runtime requalification is PASS only when R1-R7 are PASS. Host CI alone is insufficient because M1.3 changed native scanner arithmetic and user-visible CLI output.

Until the runtime record below is filled, this milestone remains `UNVERIFIED` for KS1.2 runtime despite green host CI.

## Result record

Tested commit: `cfd7b5c6bb5c03adc17bc3b4c185c97132eecaf3` or a later commit containing only qualification documentation/evidence changes.

| Gate | Result | Evidence |
| --- | --- | --- |
| R1 Baseline build | UNVERIFIED | |
| R2 Valid DOS → STANDARD | UNVERIFIED | |
| R3 Invalid checksum DOS → UNKNOWN | UNVERIFIED | |
| R4 Custom unknown → UNKNOWN | UNVERIFIED | |
| R5 Read-only hashes unchanged | UNVERIFIED | |
| R6 KS1.2 / 512 KiB runtime | UNVERIFIED | |
| R7 10x repeatability | UNVERIFIED | |

Also record:

- starting/final HEAD and `origin/main`
- divergence
- compiler/toolchain version
- FS-UAE version/profile
- Kickstart/Workbench versions
- RAM
- binary size
- test-image SHA-256 values
- screenshot/log paths where applicable

Do not tag or create a release as part of this requalification.
