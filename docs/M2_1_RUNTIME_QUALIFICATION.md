# M2.1 — Kickstart 1.2 runtime qualification

## Runtime result: PASS — 2026-09-07

R1–R10 PASS on the tested main revision. No functional code changes, temporary
branch, release or tag were needed. Final-HEAD CI is checked after pushing the
documentation commit; overall completion requires that CI to be successful.

## Repository/build (R1)

- Starting HEAD / tested HEAD / starting origin/main: `d7fe4749fb8e5b39d7a8cd16db7a7eb1015f481d`.
- Starting divergence: `0 0`; working tree clean.
- Baseline GitHub CI [34060896967](https://github.com/Ploos-AS/AmiGuard/actions/runs/34060896967)
  completed/success on this exact baseline before runtime launch.
- Final HEAD: the documentation/evidence commit containing this record,
  resolved by `git log -1 --format=%H -- docs/M2_1_RUNTIME_QUALIFICATION.md`.
  Its own hash cannot be embedded in its contents. The final commit SHA,
  origin/main, divergence, worktree status and exact-HEAD CI run/result are
  verified after push and provided in the execution response.
- `make clean`, `make check`, native `make`: PASS.
- **4 C test executables** PASS: scanner (14 reported assertions), trackdisk,
  HUNK (`hunk parser tests: PASS`), file intake (`file intake tests: PASS`).
  **47 Python tests** PASS. Signature metadata/table check PASS. Expected
  negative promotion test emits a rejection; the test suite itself passes.
- Bebbo `/opt/amiga/bin/m68k-amigaos-gcc`: `m68k-amigaos-gcc (GCC) 6.5.0b 20260807212032`.
- Native flags: `-Isrc -O2 -Wall -Wextra -Werror -m68000 -mcrt=nix13`;
  CPU/runtime flags also present on the final link.
- Size: **19012 bytes**. SHA-256: `b6f4f82a9afc0ee3dc9eafd89f5149df9972677964e5961c96861f6bd53ce8d2`.
- Amiga loadseg executable; objdump `architecture: m68k:68000`.

## Visible minimum runtime (R2)

FS-UAE **3.2.35**, existing **a500-stock-accurate** reference configuration
with a disposable overlay in `/tmp/amiguard-m21-final/runtime.fs-uae`.
A500 / Motorola 68000 / Kickstart **1.2 (33.180)** / Workbench **1.2 (33.56)**,
**512 KiB Chip RAM**, zero Fast/Slow/motherboard RAM. Original profile and ROM
were unchanged. Zero stale emulator processes were found before launch;
exactly **one visible FS-UAE window** was enforced by every GUI operation.
No headless display. Normal CLI startup and exit, no missing library/API,
OS 2.x dependency, crash, hang or Guru observed. startup.png records versions
and normal CLI output. Exec library 33.192 / DOS 33.124 are library revisions,
not the Kickstart ROM revision.

## R1–R10

| Gate | Result | Evidence |
| --- | --- | --- |
| R1 Repository/build | PASS | build.log, manifest.json, binary-format.txt |
| R2 Minimum native startup | PASS | startup.png, start-probe.log, emulator logs/config |
| R3 VALID-HUNK | PASS | filevalid.log / filevalid.png; return code 0 |
| R4 NOT-HUNK | PASS | fileplain.log / fileplain.png; return code 0 |
| R5 MALFORMED-HUNK | PASS | filemalformed.log / filemalformed.png; return code 0 |
| R6 Controlled errors | PASS | fileoversize and filemissing logs/screenshots; return code 20 for both |
| R7 Stability | PASS | 10/10 each VALID-HUNK, NOT-HUNK, MALFORMED-HUNK; all return code 0; stable Chip RAM |
| R8 Read-only integrity | PASS | all four file SHA-256 pairs identical; read-only source inspection |
| R9 Bootblock regression | PASS | clean.log: STANDARD; customone/customtwo.log: CUSTOM; all 1024-byte reads at offset 0 |
| R10 Semantic safety | PASS | neutral structural outputs; no malware verdict or file modification |

## File fixtures and observed native output (R3–R6)

All fixtures were generated on the host before launch under
`/tmp/amiguard-m21-final/fixtures/`, mode 0444, available through the
explicitly read-only AGFiles mount (`hard_drive_1_read_only = 1`). Output logs are separate from input files.
The native commands used `AmiGuard FILE AGFiles:<name>`; DOS 1.2
redirection precedes the FILE argument and Type displays each result.

- valid.hunk: 40 bytes, ten big-endian words matching tests/test_hunk.c:
  `1011,0,1,0,0,1,1001,1,0x4e754e75,1010`.
- plain.txt: 24 bytes of harmless ASCII (`Harmless ASCII fixture.` plus newline).
- malformed.hunk: four bytes, HUNK_HEADER 1011 only; intentionally truncated.
- oversize.bin: 131073 zero bytes, one byte above the 128 KiB limit.
- does-not-exist: absent path; no file was created by the test.

Exact classification/error lines observed:

```text
VALID-HUNK: supported Amiga HUNK structure (40 bytes)
NOT-HUNK: not an Amiga HUNK file (24 bytes)
MALFORMED-HUNK: HUNK structure is malformed or unsupported (4 bytes)
ERROR: file exceeds 128 KiB M2.1 limit (131073 bytes)
ERROR: cannot open file read-only
```

## Stability (R7)

Thirty repeated FILE invocations completed in the same visible 512 KiB
session: ten per classification. Each had deterministic output and return
code 0. Free Chip RAM before and after each individual scan:

- validseries: 351608 bytes before and after all ten scans (delta 0).
- plainseries: 351608 bytes before and after all ten scans (delta 0).
- malformedseries: 351608 bytes before and after all ten scans (delta 0).

No progressive memory loss was observed. Source cleanup releases the input
buffer and closes the stream on success and error paths. The probe measures
free memory after each process returns, not peak allocation during parsing.

## Read-only integrity (R8)

Hashes were taken before FS-UAE launch and after all tests/normal quit.

| File | SHA-256 before | SHA-256 after |
| --- | --- | --- |
| `valid.hunk` | `97889068b21076a9ac32673bf8237e1fdaac4efe05127ec5ae1c9e98167ae6c5` | `97889068b21076a9ac32673bf8237e1fdaac4efe05127ec5ae1c9e98167ae6c5` |
| `plain.txt` | `6d8269cd7779441f30c1e1a05c78b70dce1a9c10859cdfa08d2fa3afe0057b9c` | `6d8269cd7779441f30c1e1a05c78b70dce1a9c10859cdfa08d2fa3afe0057b9c` |
| `malformed.hunk` | `8b3c48d1f5286a750e2db8c0c583b90888ff7b0f8f75833fa941f237f26482e0` | `8b3c48d1f5286a750e2db8c0c583b90888ff7b0f8f75833fa941f237f26482e0` |
| `oversize.bin` | `d281209cc72d47b090175b22621840d9eb8267d09cc05dc122bfaa759a82830f` | `d281209cc72d47b090175b22621840d9eb8267d09cc05dc122bfaa759a82830f` |

Source inspection: src/file_intake.c opens `fopen(path, "rb")`, reads via
fread/fgetc, then fclose/free. No write/create/truncate, rename, cleaning,
quarantine or deletion path exists. File mode only invokes the HUNK parser,
not signatures. src/trackdisk.c issues only CMD_READ. No real malware,
VirusZ, Zeeball, EICAR or xvs.library was used.

## Bootblock regression (R9)

Known-clean Workbench copy still produced:

```text
trackdisk.device: read 1024 bytes at offset 0
STANDARD: Amiga DOS bootblock (valid checksum)
```

The existing harmless valid non-DOS fixture produced:

```text
CUSTOM: custom bootblock (valid checksum)
```

The reused harness additionally passed 10 STANDARD and 5 CUSTOM repeated
scans, two invalid-DOS UNKNOWN scans and the invalid-non-DOS UNKNOWN scan.
All ADFs were mode 0444, with writable_floppy_images=0 and
uae_floppy_write_protect=true. Hash pairs:

| ADF | SHA-256 before | SHA-256 after |
| --- | --- | --- |
| `workbench12.adf` | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` |
| `unknown.adf` | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` |
| `invalid.adf` | `2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` | `2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` |
| `valid-custom.adf` | `b4dac9336ac52879830f1a7b14f5bcd8cb4ace32e5dcd9c207019467017382d0` | `b4dac9336ac52879830f1a7b14f5bcd8cb4ace32e5dcd9c207019467017382d0` |

Original Workbench/reference ADF, ROM and profile hashes also remained
identical (manifest.json / observations.json). No copyrighted image or
fixture binary is committed, only logs, screenshots and generation code.

## Semantic safety (R10)

VALID-HUNK means structural validity within the parser's supported subset.
NOT-HUNK means input is not identified as HUNK. MALFORMED-HUNK means a
HUNK-like input failed structural validation. ERROR means intake/resource/path
failure. None is an infected, suspicious or clean verdict. No file signature
matching, heuristics, cleaning, quarantine, rename or file writing is introduced.
Existing STANDARD/CUSTOM/UNKNOWN bootblock semantics remain unchanged.

## Initial mount failure and full rerun

The first run at `/tmp/amiguard-m21-run` stopped on R3: `ERROR: cannot open
file read-only`. Fixtures were host mode 0444 inside the writable AGTest
volume. FS-UAE logged `my_open could not open (.../fixtures/valid.hunk, 2)`.
Native disassembly of fopen/freopen/open confirms `rb` uses MODE_OLDFILE
(1005), not MODE_NEWFILE or a create/truncate path. The failure was isolated
to the emulator host-filesystem mount: moving the same 0444 inputs to a
separate `hard_drive_1_read_only = 1` AGFiles volume fixed opening without
changing the native binary. The complete build and all runtime tests were
rerun in a fresh directory on the same tested SHA. Initial failure logs are
retained under initial-failure; no earlier failed-run result is counted PASS.

## Evidence / blockers

[evidence/m2.1](evidence/m2.1/) retains the build/config/manifest, per-invocation
logs, memory probes, driver transcript and screenshots. Screenshots were
visually checked against the logs; the generic observations.json reminder
is not automatic visual approval. Disposable full run: `/tmp/amiguard-m21-final/`.
The reused harness's empty-drive error 29 is an expected separate negative
test. Xlib BadWindow on normal quit is a key-release event after the window
closes, after completed tests; it is not an AmiGuard crash.

Blockers: **none**. Runtime R1–R10 PASS; final GitHub CI completion/success on
the documentation commit must be verified before declaring M2.1 complete.
