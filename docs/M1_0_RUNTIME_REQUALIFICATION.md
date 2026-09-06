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

### Execution record (2026-09-06)

Starting HEAD: `c632f4dafcf8dd1c2258ea8f841c60131980d3ad` (also
`origin/main`, divergence `0 0`). Tested commit is the same SHA on `main`.
Host tests and native build were run with `/opt/amiga/bin/m68k-amigaos-gcc`
GCC `6.5.0b 20260807212032`; the AmigaOS loadseg executable is 13,976 bytes
and was built with `-m68000 -mcrt=nix13`.

The existing visible FS-UAE 3.2.35 `a500-stock-accurate` profile was used:
Motorola 68000, Kickstart 1.2 (33.180), Workbench 1.2 (33.56), 512 KiB Chip
RAM, no Fast/Slow RAM. Evidence is retained in
`/tmp/amiguard-m1-run/evidence/` and screenshots in its `screenshots/`
directory. The Workbench ADF SHA-256 was
`1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` before
and after scanning. The harmless custom fixture was
`9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` before
and after.

The visible session observed successful CLI startup, a valid DOS bootblock
classified `KNOWN`, a custom bootblock classified `UNKNOWN`, and 10/10
repeated valid scans with stable free Chip RAM (359,520 bytes). After closing
all stale FS-UAE windows, one and only one visible emulator instance was used
for R3. A disposable copy derived from the known-clean Workbench image kept
the `DOS` magic (`DOS` at bytes 0–2); exactly one bootblock byte (offset 100)
was changed. Its SHA-256 was
`2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` before
and after both scans. The emulator output was `UNKNOWN: Amiga DOS bootblock
(invalid checksum)` on both scans, with no `KNOWN`, `INFECTED`, or `ERROR`.
Host regression tests also PASS invalid-checksum DOS → UNKNOWN.

All mandatory gates R1–R6 are now PASS; M1.0 runtime requalification is
complete.

Fill in after execution:

| Gate | Result | Evidence |
| --- | --- | --- |
| R1 Baseline build | PASS | `make clean && make check && make`; all host tests pass; native 68000 build succeeds. |
| R2 Valid DOS → KNOWN | PASS | Visible FS-UAE output: 1024-byte read and `KNOWN: Amiga DOS bootblock (valid checksum)`. |
| R3 Invalid checksum DOS → UNKNOWN | PASS | One visible `a500-stock-accurate` FS-UAE instance after stale-window cleanup; two scans output `UNKNOWN: Amiga DOS bootblock (invalid checksum)`. |
| R4 Custom unknown → UNKNOWN | PASS | Visible FS-UAE output: `UNKNOWN: unknown bootblock`. |
| R5 Read-only hashes unchanged | PASS | Workbench and custom ADF SHA-256 unchanged before/after. |
| R6 KS1.2 / 512 KiB runtime | PASS | Workbench boot, CLI start, DF0 read, and repeated scans observed in 512 KiB profile. |

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
