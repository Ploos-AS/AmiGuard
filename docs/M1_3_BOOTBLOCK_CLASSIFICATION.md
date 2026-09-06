# M1.3 Bootblock classification baseline

M1.3 strengthens the bootblock engine while real malware samples are not yet available.

## Changes

- Bootblock checksum arithmetic is explicitly constrained to 32 bits on both the Amiga target and wider host platforms.
- End-around carry is preserved after each 32-bit addition.
- Host regression coverage includes a carry-wrap fixture using two `0xffffffff` words.
- A checksum-valid Amiga DOS bootblock is reported as `STANDARD`, not `KNOWN`.

## Semantics

`STANDARD` means that the block has an Amiga DOS identifier and a structurally valid Amiga bootblock checksum. It does **not** mean that AmiGuard has proven the disk malware-free.

`UNKNOWN` remains the safe result for unrecognized/custom bootblocks and DOS bootblocks with an invalid checksum.

`INFECTED` remains reserved for a matching compiled signature. At present the repository contains synthetic test signatures only; no historical malware family is promoted to `verified` without sample-backed qualification.

## Compatibility

The implementation remains C89-oriented and targets Kickstart 1.2+ / Motorola 68000. No OS 2.x API dependency is introduced by this milestone.

Because `src/scanner.c` and the native CLI output changed, the next runtime gate should include a visible FS-UAE A500/Kickstart 1.2 sanity qualification before a release is considered.
