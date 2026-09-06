# M0.3 Runtime Qualification

## Result and source identity

**PASS — mandatory Gates A–E and the 512 KiB Gate F**, observed on
2026-09-06 in visible FS-UAE sessions. The safe unknown-bootblock test also passed.
No release or tag is part of this qualification.

- Initial local HEAD: `2759ae91aaab924e89e155fa5553b9fe0c024c46`, branch `main`, clean.
- After `fetch`, `checkout main`, `pull --ff-only origin main`:
  `a9d5756f17199141b24f6fab9970175ef766c2c5`; HEAD = origin/main; status empty.
- Qualification base commit: `a9d5756f17199141b24f6fab9970175ef766c2c5` **plus the
  native fixes in this change**. This is not a claim that the unmodified base
  passed. [manifest.json](evidence/m0.3/manifest.json) records the tested native
  source hashes, compiler, binary hash and working-tree status.
- Binary: 13,648 bytes; SHA-256
  `ace7b44c2ab87cfd4b2848a969b9e63d2fb1ab6f094362ee0c01931ce1385f6f`.

## Environment

| Item | Observed configuration |
| --- | --- |
| Host | Linux x86-64; visible XWayland desktop |
| Compiler | `/opt/amiga/bin/m68k-amigaos-gcc` |
| Compiler version | GCC `6.5.0b 20260807212032` |
| Native build | `make clean && make check && make`; compile and link use `-m68000 -mcrt=nix13` |
| Emulator | FS-UAE `3.2.35`, Debian package `3.2.35-2` |
| Reference | Existing Ploos-AS `FS-UAE_Config/fs-uae-amiga-reference-configs/a500/stock/a500-stock-accurate.fs-uae` |
| Model / CPU | A500, Motorola 68000; cycle-exact, JIT/FPU/MMU disabled |
| RAM | 512 KiB Chip, zero Slow/Fast/motherboard expansion RAM |
| Kickstart | 1.2; `Version` reports 33.180; Exec 33.192, DOS 33.124 |
| Workbench | 1.2, 33.56; original ADF volume `Workbench1.2` |
| Boot / program transfer | Disposable host volume `AGTest:`; original Workbench commands/libraries read from write-protected DF0 copy; `LoadWB`, then `NewCLI` |
| DF0 | Byte-identical copy of local `amiga-os-120-workbench.adf`, 901,120 bytes |
| Unknown media | New nonbootable ADF: first 1024 bytes `0x5a`, remaining bytes zero; derived from existing `tests/test_scanner.c` fixture; inserted only after boot |

The ROM, reference profile and original Workbench ADF are unchanged. All host
volume files, extracted OS commands and generated media live outside the checkout
in a new `/tmp/amiguard-m03-*` directory. No ROM or OS media is redistributed.

The saved [configuration](evidence/m0.3/runtime.fs-uae),
[resolved UAE settings](evidence/m0.3/debug.uae) and
[emulator log](evidence/m0.3/fs-uae.log.txt) identify the actual run. UAE
`chipmem_size=1` means 512 KiB; `fastmem_size=0`, `bogomem_size=0` and
`cpu_model=68000` are recorded. The host allocation log's larger backing buffer
is not the emulated RAM size. `kickshifter=false`; no ROM-file patch was used.

## Gates and observed evidence

| Gate | Result | Observed result and evidence |
| --- | --- | --- |
| Baseline host tests | PASS | Original four scanner checks passed before runtime work; final suite also covers trackdisk errors, short reads and cleanup. [Build log](evidence/m0.3/build.log) |
| Native 68000 build | PASS | Amiga LoadSeg/HUNK executable, `m68k:68000`, no unresolved symbols. [Static audit](evidence/m0.3/static-audit.txt) |
| A: CLI start | PASS | Banner, target and usage; return code 10, normal CLI prompt, no Guru/library/device failure. [Screenshot](evidence/m0.3/startup.png), [output](evidence/m0.3/start.log), [return code](evidence/m0.3/start-probe.log) |
| C: invalid targets | PASS | `DH0:`, `DF4:`, `nonsense`: usage and return code 10 each; no read-path message. [Screenshot](evidence/m0.3/invalid.png), [DH0](evidence/m0.3/dh0.log), [DF4](evidence/m0.3/df4.log), [nonsense](evidence/m0.3/nonsense.log); corresponding `*-probe.log` files record return codes |
| D: empty DF0 | PASS | Emulator ejected DF0; read error 29, return code 20, normal CLI return. [Screenshot](evidence/m0.3/empty.png), [output](evidence/m0.3/empty.log), [return code](evidence/m0.3/empty-probe.log) |
| B: real DF0 bootblock read | PASS | `trackdisk.device: read 1024 bytes at offset 0`, `KNOWN: Amiga DOS bootblock`, return code 0. Success is printed only after OpenDevice/DoIO succeed and `io_Actual == 1024`. [Screenshot](evidence/m0.3/clean.png), [output](evidence/m0.3/clean.log) |
| Read-only / media integrity | PASS | Both ADFs explicitly write protected in emulator log; original and copy hashes unchanged after emulator exit. Source/disassembly submit only `CMD_READ`, offset 0, length 1024. [Before](evidence/m0.3/manifest.json), [after](evidence/m0.3/observations.json) |
| Safe custom bootblock | PASS | `UNKNOWN: unknown bootblock`, return code 0; no INFECTED classification, rewriting or repair. [Screenshot](evidence/m0.3/custom.png), [output](evidence/m0.3/custom.log) |
| E: 10 repeated scans | PASS | 10/10 KNOWN, 1024 bytes, return code 0 in one session. Free Chip RAM 359,520 bytes before and after every scan; zero Fast RAM. [Screenshot](evidence/m0.3/repeat.png), `repeat-01.log`–`repeat-10.log`, `memory-01.log`–`memory-10.log` |
| DF0 after repetition/media swaps | PASS | Workbench DF0 directory listed normally, return code 0. [Screenshot](evidence/m0.3/post.png), [listing](evidence/m0.3/df0-after.log), [return code](evidence/m0.3/post-probe.log) |
| F: 512 KiB | PASS | Both startup and DF0 scan succeeded in the same 512 KiB profile. No RAM increase was used. |

Screenshots were opened and visually reviewed, not merely generated. They show
an active Workbench CLI and return to its prompt. Runtime logs and return codes
support each stage; `RETURNED` markers alone do not imply PASS. Committed text
logs have trailing whitespace removed; raw originals remain in the run directory.

## Media checksums (SHA-256, before = after)

| Input | SHA-256 |
| --- | --- |
| Workbench original and DF0 copy | `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0` |
| Unknown fixture ADF | `9acd344236c1d414a85b56d23b322db62023feb48df642720aaa08697e873fbd` |
| Kickstart ROM file | `781a36914b49642ab14b5a6f1e7263c7fc2dcbaba3c1fc141a163fd5299b976d` |
| Reference profile | `c280801f4129654f7dcd2dd4abf237a1d9c350dec5320b67d134154dcc43d3d4` |

## Fixes and unsuccessful setup attempts

1. GNU make's built-in `CC=cc` defeated `CC ?= m68k-amigaos-gcc`; initial `make`
   failed because host `cc` rejects `-m68000`. The Makefile now replaces the
   built-in default while preserving explicit compiler overrides.
2. Original `Printf` calls both failed native warning checks and used DOS V36
   APIs, unavailable on 1.2. They are replaced with C `printf` linked against
   `nix13`; compile and link both select this pre-2.0 runtime. See the
   [official VPrintf/Printf API documentation](https://developer.amigaos3.net/autodocs/dos.library/VPrintf.html).
3. Added the `amiga.lib` prototypes for CreatePort/CreateExtIO and their cleanup
   functions. A successful but short DoIO transfer is now rejected before scanning.
4. An early host-volume boot lacked correct Workbench assigns: `LoadWB` produced
   recoverable alert `31038009.48454C50` (Workbench opening icon.library).
   [Screenshot](evidence/m0.3/boot-setup-failure.png). This was a setup failure,
   not evidence of AmiGuard starting or crashing.
   The disposable bootstrap now assigns Workbench's SYS/LIBS/DEVS/L/FONTS before
   `LoadWB` and `NewCLI`. The original Workbench floppy also booted successfully
   without this bootstrap ([screenshot](evidence/m0.3/workbench12.png)).
   No acceptance criterion was relaxed.
5. Initial X11 input focus and direct window capture were unreliable under
   XWayland. Automation now requests desktop activation, checks the active
   FS-UAE window before input, and uses FS-UAE's own frame capture. It does not
   rely on stale XGetImage window contents. CLI redirection is placed before
   command arguments for DOS 1.2 compatibility.

## Reproduce

Use a visible desktop with FS-UAE and the tested cross compiler on PATH.
Install the host-only helpers into a temporary environment:

```sh
python3 -m venv /tmp/amiguard-tools
/tmp/amiguard-tools/bin/pip install amitools==0.8.1 python-xlib==0.33
make clean
make check
make
/tmp/amiguard-tools/bin/python scripts/m03_runtime.py \
  --reference /path/to/a500-stock-accurate.fs-uae \
  --rom /path/to/amiga-os-120.rom \
  --workbench /path/to/amiga-os-120-workbench.adf \
  --xdftool /tmp/amiguard-tools/bin/xdftool \
  --run-dir /tmp/amiguard-m03-new-run
```

The run directory must not already exist. Use your locally licensed ROM/media;
the script does not download them. `--prepare-only` creates a reviewable setup
without launching it. All builds, scripts, staged binaries, snapshots, per-call
logs and checksums are retained in the run directory. The script leaves the
emulator visible on failure and exits it after successful log checks.

F6 ejects DF0, F7 inserts the Workbench copy, F8 inserts the nonbootable fixture.
The unknown fixture is never booted. `m03_probe.c` observes previous CLI return
code, library versions and `AvailMem` using 1.x APIs; it never opens a disk device.
The script requires zero measured memory loss; a mismatch stops qualification
for investigation. Review all screenshots, actual CPU/RAM/ROM settings and hash
results before marking runtime gates PASS. See [FS-UAE input mapping](https://fs-uae.net/docs/input-mapping/)
and [hard-drive priority](https://fs-uae.net/docs/options/hard-drive-0-priority/).

## Limits

- No physical Amiga was tested. The extra host filesystem is the transfer/logging
  mechanism; DF0 scanning itself uses trackdisk.device.
- `KNOWN` currently recognizes the DOS header, not every byte of canonical boot
  code. This is a runtime qualification, not proof of malware-detection coverage
  or a general cleanliness certificate for arbitrary DOS-prefixed disks.
- Read-only evidence combines unchanged full-image hashes, emulator write
  protection and the inspected single-CMD_READ path; no independent device-bus
  trace was captured. Hashes alone cannot prove absence of attempted writes.
- Memory evidence is a stable post-process AvailMem measurement across ten runs,
  not a proof against every possible leak or a measurement of peak usage.
- Raw disassembly includes strings in executable hunks; apparent newer opcodes
  decoded from string bytes are not treated as executed instructions. CPU flags,
  base multilib selection and the actual 68000 runtime provide additional evidence.
- No blockers remain for these gates. No real malware, repair, tag or release
  was used.
