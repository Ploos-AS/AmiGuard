# M2.0 — Kickstart 1.2 runtime requalification

## Result: PASS — 2026-09-06

All mandatory R1–R9 gates PASS. Numbering follows the execution request,
superseding the draft gate numbering. No functional changes were needed.
No release, tag, or temporary branch was created.

## Repository and build

- Starting HEAD / tested HEAD / starting origin/main: `8154b1b048727d5e49b59b57241ed9b356d459d6` (`main`).
- Baseline `8154b1b048727d5e49b59b57241ed9b356d459d6` is an ancestor.
- Starting divergence: `0 0`; working tree clean (`git status --short` empty).
- Final HEAD: the documentation/evidence commit containing this record,
  resolved by `git log -1 --format=%H -- docs/M2_0_RUNTIME_REQUALIFICATION.md`.
  A commit cannot contain its own hash. Final HEAD, origin/main, divergence
  and clean worktree are verified after push and reported in the final response.
- Bebbo `/opt/amiga/bin/m68k-amigaos-gcc`: `m68k-amigaos-gcc (GCC) 6.5.0b 20260807212032`.
- `make clean`, `make check`, `make` with the Bebbo compiler: PASS.
- All host C tests PASS; all 47 Python tests PASS; signature metadata consistent.
  The promotion-gate rejection in build.log is an expected negative test.
- Explicit host output: `PASS: checksum preserves 32-bit end-around carry on wide hosts`
  and `PASS: valid non-DOS bootblock classified custom`.
- Native executable: **15,012 bytes**; compile/link flags
  `-m68000 -mcrt=nix13`; objdump architecture `m68k:68000`, Amiga loadseg format.
- Binary SHA-256: `32c72315081b5379cd7c8c34caf340017909c42bd664f634ad52b2306d1b2505`.

## Runtime environment

FS-UAE **3.2.35**, existing **a500-stock-accurate** profile, A500,
Motorola 68000, Kickstart **1.2 / 33.180**, Workbench **1.2 / 33.56**,
**512 KiB Chip RAM**, zero Fast/Slow/motherboard RAM. The reference profile
was read unchanged with a disposable storage/keyboard overlay. No headless
mode was used. Zero stale FS-UAE processes were found before launch;
exactly **one visible FS-UAE window** was required by every GUI operation.
The emulator was closed normally after completion.

`startup.png` shows Kickstart/Workbench versions and successful AmiGuard
startup. Probe library versions Exec 33.192 / DOS 33.124 are distinct from
the ROM revision. No crash, hang, missing API/library or OS 2.x dependency
was observed.

## Gates

| Gate | Result | Evidence |
| --- | --- | --- |
| R1 Host tests + native build | PASS | build.log, binary-format.txt, manifest.json |
| R2 Minimum visible runtime | PASS | startup.png, start-probe.log, runtime.fs-uae, emulator logs |
| R3 Valid DOS → STANDARD | PASS | clean.log / clean.png; read 1024 bytes at offset 0 |
| R4 Valid non-DOS → CUSTOM | PASS | customone.log and customtwo.log / screenshots; 2/2, return code 0 |
| R5 Invalid DOS → UNKNOWN | PASS | badone.log and badtwo.log / screenshots; 2/2, return code 0 |
| R6 Invalid non-DOS → UNKNOWN | PASS | custom.log / custom.png (legacy harness stage name); return code 0 |
| R7 Stability | PASS | repeat-01..10.log: 10/10 STANDARD; custom-repeat-01..05.log: 5/5 CUSTOM; all reads successful and return code 0 |
| R8 Read-only / safety | PASS | manifest.json and observations.json; all four media hashes unchanged |
| R9 M2.0 native integration sanity | PASS | HUNK source in Makefile/link, parser host tests PASS, native symbol and minimum-runtime evidence; details below |

Free Chip RAM before and after every STANDARD scan: **359,520 bytes**.
Free Chip RAM before and after every CUSTOM stability scan:
**359,744 bytes**. No progressive memory loss, crash or hang.
All measurements are retained in memory logs and verified-results.json.

## Observed CLI output

Each invocation was `AmiGuard DF0:` with DOS 1.2 output redirection to the
host-backed AGTest directory; individual results were displayed with Type.
All required scans include this exact prefix:

```text
AmiGuard 0.0.2 M0.2
Target: Kickstart 1.2+ / Motorola 68000
Reading DF0: bootblock (read-only)...
trackdisk.device: read 1024 bytes at offset 0
```

The four classification outputs were:

```text
STANDARD: Amiga DOS bootblock (valid checksum)
CUSTOM: custom bootblock (valid checksum)
UNKNOWN: Amiga DOS bootblock (invalid checksum)
UNKNOWN: unknown bootblock
```

Each scan contained exactly its expected classification, with no conflicting
STANDARD/CUSTOM/UNKNOWN label and no INFECTED/ERROR/KNOWN label.

## Fixtures and SHA-256

Disposable ADFs were prepared under `/tmp/amiguard-m20-run` before launching
FS-UAE. Each is mode 0444; `writable_floppy_images = 0` and
`uae_floppy_write_protect = true`. Only the known-clean Workbench copy was
booted. The other fixtures were inserted after startup and only scanned.

- workbench12.adf: copy of the same known-clean Workbench source used for M1.4.
- valid-custom.adf: first two big-endian words `0xffffffff`, all remaining
  bytes zero, total size 901120 bytes. Non-DOS; 32-bit end-around sum of the
  first 1024 bytes is `0xffffffff`. Harmless data, not a loader or malware.
- invalid.adf: disposable Workbench copy with only byte 100 XOR 1; bytes 0–3
  unchanged. Bootblock sum `0x01000000`, therefore invalid.
- unknown.adf: same harmless fixture as M1.3, 1024 bytes of `0x5a` followed
  by zeros; sum `0x5a5a5a5a`, therefore invalid non-DOS.

Host validation checks the compiled exact/masked synthetic signature
positions and confirms none of these fixtures matches. See
fixture-validation.json and retained preparation driver. No live malware
was used and no disk image is committed.

| Image | SHA-256 before | SHA-256 after |
| --- | --- | --- |
| `workbench12.adf` | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` |
| `unknown.adf` | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` |
| `invalid.adf` | `2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` | `2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` |
| `valid-custom.adf` | `b4dac9336ac52879830f1a7b14f5bcd8cb4ace32e5dcd9c207019467017382d0` | `b4dac9336ac52879830f1a7b14f5bcd8cb4ace32e5dcd9c207019467017382d0` |

Hashes were measured before emulator launch and after all scans and normal
quit. Original Workbench ADF, ROM and reference profile also remained
byte-identical; source paths/hashes are retained in the manifests.
Source inspection of src/trackdisk.c confirms the only device request is
CMD_READ; no write, format or update command was used against trackdisk.device.
The host trackdisk tests corroborate the read-only request and cleanup path.

## M2.0 native integration sanity (R9)

1. Makefile SRC includes src/hunk.c; build.log shows src/hunk.o compiled
   with `-m68000 -mcrt=nix13` and included in the final native link.
   native-symbols.txt confirms `0000078a T _amiguard_parse_hunk`.
2. `make check` builds tests/test_hunk.c with strict C89 flags and prints
   **`hunk parser tests: PASS`**. Tests exercise short/non-HUNK input,
   valid minimal CODE, truncated end and trailing malformed data.
3. This exact HUNK-linked binary ran the visible KS1.2 / 512 KiB session
   documented above. This verifies integration/startup and bootblock runtime;
   it does not claim native execution of the parser, which CLI does not call.
4. hunk.h returns only NOT_HUNK, VALID or MALFORMED. These are structural
   results; VALID is not malware-free and MALFORMED is not infected.
5. hunk.c reads an in-memory const buffer, with no file/device I/O or cleaning.
   No file-writing path or malware-detection claim was introduced.
6. main.c, scanner.c and trackdisk.c are byte-identical to the M1.4 tested
   commit d999d3f; the four observed bootblock CLI results remain unchanged.

## Final CI completion condition

R1–R9 runtime qualification is PASS. Overall M2.0 completion additionally
requires GitHub Actions CI to pass on the final documentation commit. The
post-push run ID, exact final SHA and result are verified and supplied in
the final execution response, because that run only exists after this commit.
No earlier baseline CI result substitutes for this final-HEAD check.

## Semantic acceptance

Confirmed against scanner.c, scanner.h, main.c and runtime results:

- STANDARD = DOS0–DOS7 + valid checksum, structurally standard/valid;
  **not a guarantee of a malware-free disk**.
- CUSTOM = non-DOS + valid Amiga bootblock checksum; **neutral**, neither
  suspicious nor infected.
- UNKNOWN = structure/checksum does not qualify as STANDARD or CUSTOM.
- INFECTED = **only a compiled signature match**. Signature matching takes
  precedence over structural classifications; no heuristic virus accusation
  was introduced in M2.0.

## Evidence and blockers

Committed evidence: [evidence/m2.0](evidence/m2.0/). Full disposable run:
`/tmp/amiguard-m20-run/`; GUI driver transcript: driver.log. Build, native
format, emulator configuration/logs, individual CLI/probe logs, hashes,
fixture validation and screenshots are retained. Gate screenshots were
visually reviewed against the CLI logs; the generic observations.json
human-review reminder does not imply automatic screenshot approval.

The reused harness additionally checks invalid targets and an empty drive;
the expected error 29 from the empty-drive test is separate from required
media scans. Any Xlib BadWindow messages on normal quit concern key release
after the window closes, after successful gate completion.

Blockers: **none**.
