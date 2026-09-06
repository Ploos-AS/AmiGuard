# M1.0 — Kickstart 1.2 runtime requalification

## Purpose

Requalify the M1.0 bootblock checksum/classification change on the same minimum runtime previously qualified by M0.3.

## Required environment

- FS-UAE visible, not headless
- A500
- Motorola 68000
- Kickstart 1.2 / Workbench 1.2
- 512 KiB Chip RAM
- native AmiGuard built with `m68k-amigaos-gcc -m68000`

Reuse the existing `a500-stock-accurate` profile and existing safe test media where possible. Do not modify ROMs, Workbench media, or reference profiles permanently.

## Gates

### R1 — Baseline build

Run:

```sh
make clean
make check
make
```

Expected: host tests PASS and native build PASS.

### R2 — Known valid DOS bootblock

Boot the visible A500/Kickstart 1.2 environment with the same known-clean test floppy/ADF used during M0.3.

Run:

```text
AmiGuard DF0:
```

Expected:

- `trackdisk.device` read succeeds;
- exactly 1024 bytes are read;
- classification is `KNOWN`;
- no crash/hang;
- no media change.

Record SHA-256 of the test image before and after if the image is host-accessible.

### R3 — Invalid-checksum DOS bootblock

Create or reuse a harmless test copy derived from a known-clean DOS bootblock. Corrupt one non-header byte in a copy so the `DOS` identifier remains intact while the checksum becomes invalid. Do not modify the original image.

Run:

```text
AmiGuard DF0:
```

Expected:

- read succeeds;
- classification is `UNKNOWN`;
- it must not be reported as `KNOWN`;
- it must not be reported as `INFECTED`;
- no repair/write action occurs.

### R4 — Unknown custom bootblock regression

Use the existing harmless unknown/custom bootblock fixture from M0.3 if available.

Expected: `UNKNOWN`, with no crash and no media modification.

### R5 — Read-only regression

For every host-backed ADF used in R2-R4, verify SHA-256 before and after runtime testing.

Expected: all hashes unchanged.

### R6 — Minimum-runtime regression

Repeat R2 on the qualified minimum runtime:

- A500
- 68000
- Kickstart 1.2
- 512 KiB Chip RAM

Expected: PASS with no missing API/library errors and no crash/hang.

## Acceptance

M1.0 runtime requalification is PASS only when R1-R6 are PASS. Any untested mandatory gate remains `UNVERIFIED`; do not infer PASS from host tests.

## Result record

Fill in after execution:

| Gate | Result | Evidence |
| --- | --- | --- |
| R1 Baseline build | UNVERIFIED | |
| R2 Valid DOS → KNOWN | UNVERIFIED | |
| R3 Invalid checksum DOS → UNKNOWN | UNVERIFIED | |
| R4 Custom unknown → UNKNOWN | UNVERIFIED | |
| R5 Read-only hashes unchanged | UNVERIFIED | |
| R6 KS1.2 / 512 KiB runtime | UNVERIFIED | |

Also record:

- tested commit SHA;
- compiler/toolchain version;
- FS-UAE version/profile;
- Kickstart/Workbench versions;
- RAM;
- binary size;
- test-image hashes;
- screenshots/log paths where applicable.

Do not tag or create a release as part of this requalification.
