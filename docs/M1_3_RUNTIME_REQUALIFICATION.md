# M1.3 — Kickstart 1.2 runtime requalification

## Result: PASS (2026-09-06)

All mandatory R1–R8 gates below PASS. This record uses the gate numbering
requested for this run, superseding the earlier seven-gate draft.
No functional changes, release, tag or temporary branch were needed.

## Revision and build

- Starting/tested HEAD: `15b900ae294c2b91f2e2ae26cdba8f7be73c7805` on `main`.
- Starting `origin/main`: `15b900ae294c2b91f2e2ae26cdba8f7be73c7805`.
- Contains M1.3 baseline `cfd7b5c6bb5c03adc17bc3b4c185c97132eecaf3`.
- Starting divergence: `0 0`; `git status --short`: empty.
- Final HEAD: the documentation/evidence commit containing this record
  (`git log -1 --format=%H -- docs/M1_3_RUNTIME_REQUALIFICATION.md`).
  Its own hash cannot be embedded in its contents. Final remote SHA and
  divergence are verified after push and reported in the execution response.
- `/opt/amiga/bin/m68k-amigaos-gcc` (Bebbo), GCC `6.5.0b 20260807212032`.
- `make clean`, `make check`, `make`: PASS with toolchain on PATH.
- Signature metadata/table consistent; all scanner and trackdisk host tests
  PASS; all 18 Python tests PASS. The promotion rejection message is an
  expected negative-test result, not a build failure.
- Native binary: **14,056 bytes**, `-m68000 -mcrt=nix13` on compile and link;
  objdump confirms `architecture: m68k:68000`, Amiga loadseg format.
- Binary SHA-256: `2f435c88a14cbc4ae901813bcffff99c4edb2f4fa63fbfb4a0fb65f621ca4085`.

## Visible environment

FS-UAE **3.2.35**, existing `a500-stock-accurate` reference profile with a
separate disposable storage/keyboard overlay in `/tmp/amiguard-m13-run`.
A500, Motorola 68000, **512 KiB Chip RAM**, zero Fast/Slow/motherboard RAM.
Kickstart **1.2 (33.180)** and Workbench **1.2 (33.56)** are visible in
`startup.png`; emulator ROM identification corroborates Kickstart. Probe
reports Exec 33.192 / DOS 33.124 (library revisions, not ROM revision).

There were zero stale FS-UAE processes before launch, exactly **one visible
FS-UAE window** during every GUI operation (enforced by existing
`scripts/m03_gui.py`), and zero emulator processes after normal quit.
No headless display was used. Startup and scans returned without crash,
hang, missing library/API or OS 2.x dependency errors.

## Gates

| Gate | Result | Actual evidence |
| --- | --- | --- |
| R1 Host + native build | PASS | `build.log`, `binary-format.txt`, `manifest.json` |
| R2 Visible KS1.2 start | PASS | `startup.png`, `start.log`, `start-probe.log`, emulator logs/config |
| R3 Valid DOS → STANDARD | PASS | `clean.log`, `clean.png`; 1024-byte read at offset 0; no KNOWN/INFECTED/ERROR |
| R4 Invalid checksum DOS → UNKNOWN | PASS | `badone.log`, `badtwo.log` and screenshots; both return code 0; no STANDARD/INFECTED/ERROR |
| R5 Custom bootblock | PASS | `custom.log`, `custom.png`; return code 0, no crash/hang |
| R6 Repeated stability | PASS | `repeat-01.log` through `repeat-10.log`: 10/10 reads, STANDARD and return code 0 |
| R7 Checksum portability | PASS | Host output: `PASS: checksum preserves 32-bit end-around carry on wide hosts` |
| R8 Read-only | PASS | All three before/after SHA-256 pairs below identical |

R7 uses the existing host fixture in `tests/test_scanner.c`: two
`0xffffffff` words produce `0xffffffff` with 32-bit end-around carry.
No runtime virus fixture or real-media bootblock write was used.

Free Chip RAM was **359,520 bytes** before the ten-scan series and after
each of its ten scans (`repeat-before.log`, `memory-01.log` through
`memory-10.log`); free Fast RAM was zero. No progressive memory loss observed.

## Observed Amiga CLI output

Each scan executes `AmiGuard DF0:` with output redirected to AGTest and
shown using `Type`; redirection precedes arguments for DOS 1.2 compatibility.
The common prefix is:

```text
AmiGuard 0.0.2 M0.2
Target: Kickstart 1.2+ / Motorola 68000
Reading DF0: bootblock (read-only)...
trackdisk.device: read 1024 bytes at offset 0
```

Valid DOS (initial scan and all ten repetitions):

```text
STANDARD: Amiga DOS bootblock (valid checksum)
```

Invalid checksum DOS (two scans):

```text
UNKNOWN: Amiga DOS bootblock (invalid checksum)
```

Harmless custom fixture:

```text
UNKNOWN: unknown bootblock
```

## Read-only media evidence

All images are disposable, host-backed ADFs under `/tmp/amiguard-m13-run`,
mode 0444, with `writable_floppy_images = 0` and
`uae_floppy_write_protect = true`. The known-clean image is copied from the
same Workbench source used for M1.0. The custom fixture reproduces the earlier
harmless 1024-byte `0x5a` bootblock with a zero-filled remainder; its hash is
identical to the previous fixture. It was inserted after boot, never executed.
The invalid image is a copy of the clean image with only byte 100 XOR 1;
bytes 0–3 remain unchanged. Hashes were taken before launching and after quit.

| Image | SHA-256 before | SHA-256 after |
| --- | --- | --- |
| `workbench12.adf` | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` |
| `unknown.adf` | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` |
| `invalid.adf` | `2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` | `2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` |

Original Workbench ADF, ROM and reference profile hashes also remained
unchanged; full input paths and hashes are in `manifest.json` and
`observations.json`.

## Retained evidence and observations

Evidence is committed in [evidence/m1.3](evidence/m1.3/), including build,
per-scan/probe and emulator logs, the configuration, manifests and screenshots.
The disposable preparation/runtime drivers are retained for audit alongside
the evidence; they adapt the existing M0.3 harness to STANDARD and add two
invalid-checksum scans. Local full working data: `/tmp/amiguard-m13-run/`.
Screenshots startup, clean, badone, badtwo, custom and repeat were visually
reviewed against the logs; the harness JSON's generic human-review reminder
is not an automated visual approval.

The reused harness also exercised invalid targets and an empty drive; the
expected empty-drive error 29 visible above the clean result is from that
separate negative test. All mandatory media scans succeeded. Xlib emitted
BadWindow on key release during normal emulator quit; this occurred after
all scans and screenshots. An extra screenshot request reached the desktop
after quit and correctly found zero windows; existing gate screenshots are
complete. Neither is an AmiGuard failure.

Blockers: **none**.
