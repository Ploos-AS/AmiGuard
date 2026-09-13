# AmiGuard v0.1.0 native qualification

**PASS — 2026-09-13.** AmiGuard was qualified in visible, non-headless
FS-UAE sessions on an A500 / Motorola 68000 / Kickstart 1.2 / Workbench 1.2
profile with 512 KiB Chip RAM. No AmiGuard code or detection semantics were
changed during qualification, and no repair or delete operation was invoked.

## Qualified source and binary

- Qualified `main` HEAD: `95ea9491f0d7d79367cf28142a0fb4229712b6cd`.
- The worktree was clean and `main` matched `origin/main` before the build.
- Host gate: `make check` — PASS (five C suites and 107 Python tests).
- Native build command: `make CC=/opt/amiga/bin/m68k-amigaos-gcc` after
  `make clean`.
- Compiler: `/opt/amiga/bin/m68k-amigaos-gcc`,
  `m68k-amigaos-gcc (GCC) 6.5.0b 20260807212032`.
- Native compile/link flags: `-m68000 -mcrt=nix13`; native XVS bridge compile
  define: `-DAMIGUARD_NATIVE_XVS=1`.
- Binary: AmigaOS loadseg executable, `m68k:68000`, 21,276 bytes.
- AmiGuard SHA-256:
  `4a411c257dfb63e0160bcf8524f7640c3445a88f5a970793d10ac8b91d2cea4c`.

The repository binary and both staged runtime copies had that same digest
after testing. The observed banner is exactly `AmiGuard 0.0.2 M2.3`; the CLI
then identifies the target as Kickstart 1.2+ / Motorola 68000 and prints both
the bootblock and FILE forms of the command.

## Visible runtime

- FS-UAE 3.2.35, visible 960 x 720 window; `window_hidden = 0` and
  `window_minimized = 0`. The GUI driver refused input unless exactly one
  visible FS-UAE window was active. No headless run was used.
- Reference profile: `a500-stock-accurate`, A500, 68000, cycle-exact, no JIT.
- Kickstart 1.2 / 33.180 and Workbench 1.2 / 33.56, shown by the native
  Workbench `Version` command in both startup screenshots.
- 512 KiB Chip RAM, zero Slow, Fast and motherboard RAM. The effective
  emulator log reports 512 KiB Chip RAM; the native probe reports
  `free-fast=0`.
- Kickstart ROM SHA-256:
  `781a36914b49642ab14b5a6f1e7263c7fc2dcbaba3c1fc141a163fd5299b976d`.
- Workbench ADF SHA-256:
  `1035a9a317fbbf0056848a25397f245967d7a8f1bc5079b02a018f410899bdf0`.

The ROM and Workbench media are pre-existing local legal inputs. They are not
committed. A disposable ADF copy was mode 0444, FS-UAE floppy writes were
disabled, and the emulator reported the disk write-protected. File fixtures
were on a separate read-only mounted volume.

## Qualification gates

| Gate | Result | Observed evidence |
| --- | --- | --- |
| Kickstart/Workbench 1.2 startup | PASS | Both visible startup screenshots show Kickstart 33.180 and Workbench 33.56; the native probe reports Exec/DOS/Workbench 33.x. |
| Banner and CLI | PASS | Native banner and both usage forms printed normally; return code 10 for usage. |
| `AmiGuard DF0:` read-only | PASS | `Reading DF0: bootblock (read-only)`, `read 1024 bytes at offset 0`, return code 0; no crash. |
| Standard bootblock false-positive safety | PASS | Known-clean Workbench 1.2 DF0 returned `STANDARD: Amiga DOS bootblock (valid checksum)`, never `INFECTED`. |
| `AmiGuard FILE <path>` | PASS | Read-only scan of a 48-byte harmless text file returned `NOT-HUNK`, return code 0. |
| Harmless AmiGuard test signature | PASS | Authoritative 68-byte EICAR safe-test returned `TEST-SIGNATURE: EICAR Standard Anti-Virus Test File`, never `INFECTED` or `XVS-DETECTED`. |
| `xvs.library` absent | PASS | A separate complete visible session had no staged xvs library. Startup, banner, DF0, FILE and safe-test gates passed. A read-only open probe returned `xvs-open=UNAVAILABLE` without affecting AmiGuard. |
| Absence does not change normal behavior | PASS | Startup, banner, bootblock, plain FILE, EICAR and wrapped-safe-test AmiGuard logs are byte-for-byte identical between absent and present sessions. |
| Optional local xvs open | PASS | Pre-existing local xvs 33.49, SHA-256 `d178b7770199cd2abac2bb66ee95a86880a649c98b8bb681e8255de117eee21c`, opened on Kickstart 1.2 and returned `xvs-self-test=PASS`. It was used only from an uncommitted disposable copy. |
| XVS-enabled AmiGuard path | PASS | Before the standalone probe, AmiGuard's first DF0 scan loaded the local library: post-scan free Chip RAM was 281,336 bytes versus 351,608 in the absent session, consistent with the 68,092-byte library and loader overhead. DF0 and ordinary FILE results remained unchanged. |
| XVS verdict separation | PASS | The exact binary retains both XVS bridge symbols and both XVS result strings. Source/binary audit confirms file and bootblock XVS result branches print `XVS-DETECTED` plus “not an AmiGuard INFECTED verdict”; neither calls a repair/install/delete/remove API. |
| No repair/delete | PASS | Only xvs self-test, allocation/free and check calls exist in the bridge; runtime invoked no repair or delete command. All original/media/fixture hashes checked after the sessions were unchanged. |
| Post-scan responsiveness | PASS | Both sessions completed a final Workbench directory listing and quit normally without Guru, crash or hang. |

The available harmless xvs probes (EICAR with a four-byte prefix and two local
EICAR ZIPs) were not recognized by xvs 33.49 and correctly remained
`NOT-HUNK`; therefore no runtime `XVS-DETECTED` positive is claimed. No
proprietary or malware sample was downloaded merely to force that output.
Verdict separation is instead established by the exact built binary and its
source control flow, while the optional-open and normal-scan paths are proven
in the visible native session.

## Integrity and evidence

The original reference profile, ROM, Workbench ADF, EICAR inputs and local
xvs library retained their recorded SHA-256 values. The disposable Workbench
copy, all file fixtures and both staged AmiGuard binaries also retained their
pre-run values. The complete safe evidence set is under
[evidence/v0.1.0-native](evidence/v0.1.0-native/). It includes build output,
effective FS-UAE configuration/logs, native CLI logs and return-code probes,
visually reviewed screenshots, manifests, the read-only XVS open helper and
the verdict audit. It excludes ROMs, ADFs, EICAR fixture bytes and
`xvs.library`. As in earlier repository evidence, committed text copies have
line-ending whitespace and extra blank EOF lines removed; the raw disposable
run remains under `/tmp/amiguard-v010-native-95ea949`.

The final successful GUI quit produced the already-known Xlib `BadWindow`
messages while releasing the quit chord after FS-UAE had closed. This occurred
after all checks and the final screenshot and is not an AmiGuard crash. Earlier
disposable harness/setup issues and their concrete corrections are recorded in
[attempts.md](evidence/v0.1.0-native/attempts.md); every affected runtime gate
was rerun from clean completion markers.

No tag is created by this qualification. The eventual `v0.1.0` tag remains
conditional on green CI for the final qualification documentation commit and
the other release-candidate gates.
