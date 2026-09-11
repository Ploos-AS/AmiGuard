# FS-UAE + AROS provisional CI qualification

AmiGuard uses a GitHub Actions runtime gate based on FS-UAE and the freely redistributable AROS m68k environment. This gate is intentionally **provisional**.

The workflow verifies four things on every qualifying run:

1. the existing host regression suite remains green;
2. FS-UAE can keep an AROS/internal-ROM Amiga guest running on the GitHub runner;
3. AmiGuard builds as a native 68000 Amiga executable with the pinned Bebbo toolchain image;
4. the native AmiGuard binary executes inside the AROS guest and detects a harmless synthetic `test-only` file fixture through the real `AmiGuard FILE` path.

No live malware is committed, downloaded, executed, or uploaded as CI evidence. The detector fixture is generated from AmiGuard's own synthetic test marker.

## Qualification boundary

A passing GitHub runner result proves that the native binary can execute under FS-UAE/AROS and that the file-signature path works end-to-end. It does **not** prove final Kickstart 1.2 compatibility and must not promote a research signature to verified status by itself.

Final native qualification remains a visible A500/68000/Kickstart 1.2 run using the project's canonical qualification procedure. AROS CI is the automated pre-qualification gate used before that final run.

Artifacts retain toolchain identity, native binary hash, FS-UAE version/logs, AROS source/archive hash, guest output and gate result. They must not contain malware samples.
