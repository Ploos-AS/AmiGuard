# AmiGuard v0.1.0 release notes

AmiGuard v0.1.0 is the first public release of the open-source antivirus project for classic Amiga systems.

Copyright: Ploos AS
Uploader: Per Gustav Ousdal <amiguard@ousdal.org>
License: MIT

## Highlights

- AmigaOS / Kickstart 1.2+ target.
- Motorola 68000 target with a 512 KiB-friendly runtime path.
- Read-only bootblock scanning.
- Read-only file scanning with Amiga HUNK classification.
- Test-only signature support for qualification.
- Optional transitional `xvs.library` bridge.
- xvs-only detections are clearly labelled `XVS-DETECTED`, never AmiGuard `INFECTED`.
- Community malware submission channel at https://amiguard.ploos.no/.

## Why sample submission matters

AmiGuard currently has no independently verified production malware signatures. Authentic historical samples are needed to derive, review, clean-corpus test, and visibly qualify independent AmiGuard signatures. Suspicious executables, infected or suspicious ADFs, bootblock samples, and files identified by another Amiga antivirus are especially valuable. When practical, submit a complete disk image so bootblock and disk context are preserved.

Do not attach suspected malware to GitHub issues, pull requests, discussions, or repository commits. Use the dedicated submission service instead.

## Qualification

The release candidate source was qualified in visible FS-UAE on an A500 / 68000 / Kickstart 1.2 / Workbench 1.2 profile with 512 KiB Chip RAM. The final v0.1.0 banner/packaging change must retain green CI and receive a final visible native smoke before the release tag is created.
