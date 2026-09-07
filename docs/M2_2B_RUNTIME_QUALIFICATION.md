# M2.2b — Native file signature matcher runtime qualification

## Runtime R1–R10: PASS — 2026-09-07

No code fixes, work branch, tag or release. Final GitHub CI is verified after
pushing this documentation/evidence commit; completion requires success on
that exact final SHA, reported in the execution response.

## Revision/build

- Starting HEAD / tested HEAD / starting origin/main: `809b41d10742a1015c30b0bd2d00f033a15fb16d`.
- Main matched origin/main; divergence `0 0`; clean worktree before build.
- Baseline [CI run 34090039422](https://github.com/Ploos-AS/AmiGuard/actions/runs/34090039422)
  was verified completed/success on this SHA before runtime.
- Final HEAD: the documentation/evidence commit containing this record,
  resolved by `git log -1 --format=%H -- docs/M2_2B_RUNTIME_QUALIFICATION.md`.
  A commit cannot embed its own hash. Final origin/main, clean worktree,
  divergence and exact final-HEAD CI are checked after push and reported.
- `make clean`, `make check`, native `make`: PASS.
- **5 C suites** PASS: scanner, trackdisk, HUNK, file-signature matcher,
  file intake. **53 Python tests** PASS, including six file-signature
  compiler/lifecycle tests. Bootblock and file metadata/generated checks PASS.
  The promotion rejection message is an expected negative host test.
- Bebbo `/opt/amiga/bin/m68k-amigaos-gcc`: `m68k-amigaos-gcc (GCC) 6.5.0b 20260807212032`.
- Compile flags: `-Isrc -O2 -Wall -Wextra -Werror -m68000 -mcrt=nix13`;
  link: `-O2 -Wall -Wextra -Werror -m68000 -mcrt=nix13`.
- Native binary: **19464 bytes**; SHA-256
  `46bf3e259433faf88ace1ebea1d8d9748771ebc656ea8bc7cb6a25a011c0e850`. Amiga loadseg, objdump `m68k:68000`.
- Build log shows src/file_signatures.o compiled and linked. Native symbol
  `000010e0 T _amiguard_match_file_signature` is retained in native-symbols.txt.

## Runtime environment

One visible **FS-UAE 3.2.35** instance; no stale emulator processes before
launch and every GUI operation requires exactly one visible window.
**a500-stock-accurate**, A500 / Motorola 68000, **Kickstart 1.2 / 33.180**,
**Workbench 1.2 / 33.56**, **512 KiB Chip RAM**, zero Fast/Slow/motherboard RAM.
Normal CLI startup/exit, no crash, hang, Guru, missing API/library or OS 2.x
requirement observed. startup.png documents visible versions and output.

Disposable overlay: `/tmp/amiguard-m22b-run/runtime.fs-uae`; original profile
unchanged. Fixtures reside on separate **AGFiles** volume with
`hard_drive_1_read_only = 1`, mode 0444 on host. AGTest holds binary, command
scripts and separate output logs. This reuses the working M2.1 mount method;
no writable mount fallback or fixture permission relaxation was needed.

## Gates

| Gate | Result | Evidence |
| --- | --- | --- |
| R1 Repository/build | PASS | build.log, manifest.json, binary-format.txt |
| R2 Matcher linkage | PASS | native-symbols.txt, generated include, host matcher/compiler checks |
| R3 Synthetic positive | PASS | positive.log / positive.png: TEST-SIGNATURE, never INFECTED |
| R4 Near-miss | PASS | nearmiss.log / nearmiss.png: NOT-HUNK, no TEST-SIGNATURE/INFECTED |
| R5 M2.1 regression/errors | PASS | filevalid, fileplain, filemalformed, fileoversize, filemissing logs/screenshots |
| R6 Precedence | PASS | positive begins 00000000 (NOT-HUNK header) but reports TEST-SIGNATURE |
| R7 512 KiB stability | PASS | five series of 10 scans; all deterministic, return code 0; stable Chip RAM |
| R8 Integrity | PASS | six files and four ADF SHA-256 pairs unchanged; source read-only review |
| R9 Bootblocks | PASS | STANDARD, CUSTOM and both invalid-checksum UNKNOWN cases |
| R10 Lifecycle safety | PASS | metadata/compiler/table inspection, lifecycle host tests, native TEST-SIGNATURE output |

## Fixture construction and actual native output

Generated from the repository JSON, not an assumed marker. The active record
is `amiguard-file-test-marker`, name `AmiGuard synthetic file test marker`,
status test-only, synthetic true. Pattern `AMIGUARD-FILE-TEST` is 18 bytes at
offset 4 with eighteen `ff` mask bytes. No separate size constraint; matcher
requires offset+length within input and intake caps input at 128 KiB.

Positive: four zero bytes + exact pattern, 22 bytes. Near-miss: same size,
only byte 4 XOR 1 (`41` → `40`), a fully compared byte. Both first words are
00000000, so structural fallback is NOT-HUNK. Positive matching therefore
also proves signature precedence. Exact bytes/metadata/mutation are retained
in synthetic-fixture.json and generation code.

Other fixtures: valid.hunk is the 40-byte minimal HUNK from tests/test_hunk.c;
plain.txt is 24-byte harmless ASCII; malformed.hunk is only the four-byte
HUNK_HEADER; oversize.bin is 131073 zero bytes. Missing path does-not-exist
remained absent. No live malware or external AV fixtures were used.

Commands are `AmiGuard FILE AGFiles:<fixture>`, with DOS 1.2 redirection
before FILE and Type to display results. Actual result lines:

```text
TEST-SIGNATURE: AmiGuard synthetic file test marker (22 bytes)
NOT-HUNK: not an Amiga HUNK file (22 bytes)
VALID-HUNK: supported Amiga HUNK structure (40 bytes)
NOT-HUNK: not an Amiga HUNK file (24 bytes)
MALFORMED-HUNK: HUNK structure is malformed or unsupported (4 bytes)
ERROR: file exceeds 128 KiB M2.1 limit (131073 bytes)
ERROR: cannot open file read-only
```

All classification invocations return 0; oversize and missing file return 20
without crash/hang. No tested file output contains INFECTED or CLEAN.

## Stability

All fifty repeated FILE scans ran in this same visible session. Each series
has ten expected classifications and ten return codes 0. Free Chip RAM:

| Series | Before | After each of ten scans | Delta |
| --- | --- | --- | --- |
| positiveseries (10/10) | 351608 | 351608 | 0 |
| nearmissseries (10/10) | 351608 | 351608 | 0 |
| validseries (10/10) | 351608 | 351608 | 0 |
| plainseries (10/10) | 351608 | 351608 | 0 |
| malformedseries (10/10) | 351608 | 351608 | 0 |

No progressive loss. Measurements are after each process exits, not peak
allocation. Input buffers/streams are released on match, fallback and error
paths. verified-results.json and individual memory logs retain all values.

## SHA-256 before/after

Measured before launching FS-UAE and after all scans and normal quit.

| File | Bytes | Before | After |
| --- | --- | --- | --- |
| nearmiss.bin | 22 | `ee08e8ac56d04ace7685acaa41478ffd9f58395c9076867eec26f7de3092d398` | `ee08e8ac56d04ace7685acaa41478ffd9f58395c9076867eec26f7de3092d398` |
| positive.bin | 22 | `1783b2888c51931f421dd887b3fe199a55f9f282e589c9ae805471a082cda5d3` | `1783b2888c51931f421dd887b3fe199a55f9f282e589c9ae805471a082cda5d3` |
| oversize.bin | 131073 | `d281209cc72d47b090175b22621840d9eb8267d09cc05dc122bfaa759a82830f` | `d281209cc72d47b090175b22621840d9eb8267d09cc05dc122bfaa759a82830f` |
| malformed.hunk | 4 | `8b3c48d1f5286a750e2db8c0c583b90888ff7b0f8f75833fa941f237f26482e0` | `8b3c48d1f5286a750e2db8c0c583b90888ff7b0f8f75833fa941f237f26482e0` |
| plain.txt | 24 | `6d8269cd7779441f30c1e1a05c78b70dce1a9c10859cdfa08d2fa3afe0057b9c` | `6d8269cd7779441f30c1e1a05c78b70dce1a9c10859cdfa08d2fa3afe0057b9c` |
| valid.hunk | 40 | `97889068b21076a9ac32673bf8237e1fdaac4efe05127ec5ae1c9e98167ae6c5` | `97889068b21076a9ac32673bf8237e1fdaac4efe05127ec5ae1c9e98167ae6c5` |

ADF copies are mode 0444, `writable_floppy_images=0` and
`uae_floppy_write_protect=true`. Only the known-clean Workbench copy was
booted; synthetic bootblocks were inserted after startup.

| ADF | Before | After |
| --- | --- | --- |
| workbench12.adf | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` |
| unknown.adf | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` |
| invalid.adf | `2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` | `2717ef98ca83cc1238ffa673f73d19660f76eed8925d1ccffb441e1eea35eeec` |
| valid-custom.adf | `b4dac9336ac52879830f1a7b14f5bcd8cb4ace32e5dcd9c207019467017382d0` | `b4dac9336ac52879830f1a7b14f5bcd8cb4ace32e5dcd9c207019467017382d0` |

Original Workbench image, ROM and reference profile also hash identically;
manifest.json/observations.json retain source paths and hashes.

## Bootblock regression

All reads were 1024 bytes at offset 0. Exact results:

```text
STANDARD: Amiga DOS bootblock (valid checksum)
CUSTOM: custom bootblock (valid checksum)
UNKNOWN: Amiga DOS bootblock (invalid checksum)
UNKNOWN: unknown bootblock
```

The reused harness also passed ten repeated STANDARD and five CUSTOM scans,
two invalid-DOS scans and one invalid-non-DOS scan without crash/hang.

## Read-only and lifecycle acceptance

file_intake.c uses fopen(path, "rb"), fread/fgetc, fclose/free; the matcher
only compares a const buffer against generated patterns. No file write,
create, truncate, rename, delete, quarantine or cleaning path was added.
trackdisk.c still uses CMD_READ only.

Compiler validation restricts test-only to synthetic records. It rejects
synthetic qualified/verified records; render includes only test-only and
verified. research/qualified are proven absent by host compiler tests.
Generated table currently has exactly one entry with test_only=1. Intake
maps this flag to AMIGUARD_FILE_TEST_SIGNATURE and CLI prints TEST-SIGNATURE.
Only an active verified non-synthetic record can take the file INFECTED path;
none is present or tested here. No real-malware detection claim is made.

The M2.2 framework document explicitly describes the earlier host-only step;
M2.2b's linked implementation matches its own runtime-gate contract.
VALID-HUNK remains supported structural validity only, NOT-HUNK absence of
HUNK identification, MALFORMED-HUNK failed structural validation. None is a
clean or malware verdict.

## Evidence and completion

Committed safe evidence: [evidence/m2.2b](evidence/m2.2b/), including logs,
config, manifest, generated table, fixture construction, native symbols and
visually reviewed screenshots. Full local run `/tmp/amiguard-m22b-run/`.
No ROM, Workbench/ADF image, fixture binary or malware is committed.
The generic screenshot-review reminder in observations.json is supplemented
by actual visual review. Expected empty-drive error 29 is an additional
negative harness test; Xlib BadWindow during normal quit is key release after
the completed emulator window closes, not an AmiGuard crash.

Fixes required: **none**. Blockers: **none**. Runtime R1–R10 PASS; overall
completion additionally requires final CI completed/success on this
unchanged-code documentation commit, checked after push.
