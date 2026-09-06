# M1.0 — Bootblock integrity and classification hardening

## Goal

Make AmiGuard's bootblock classification conservative enough for real antivirus work on AmigaOS/Kickstart 1.2+.

## Classification contract

AmiGuard must not treat the three-byte `DOS` identifier alone as proof that a bootblock is known-good.

For a 1024-byte Amiga floppy bootblock:

- a configured malware signature match is `INFECTED`;
- a `DOS` bootblock with a valid Amiga longword checksum is `KNOWN`/standard;
- a `DOS` bootblock with an invalid checksum is `UNKNOWN`;
- any other unrecognized bootblock is `UNKNOWN`;
- malformed input is `ERROR`.

`UNKNOWN` does not mean infected. It means AmiGuard does not have enough evidence to classify the bootblock as known-good or infected.

## Checksum

The first two floppy sectors form the 1024-byte bootblock. The bootable Amiga DOS format uses a 32-bit big-endian longword checksum with end-around carry; the sum across the complete bootblock must be `0xffffffff`.

The implementation is intentionally self-contained C89 code and does not require newer AmigaOS APIs.

## Safety

M1.0 remains read-only. It does not add repair, rewriting, formatting, or automatic cleaning.

A checksum-valid DOS bootblock is structurally valid, but that fact alone is not a malware guarantee. Future M1 milestones will add explicit known-clean fingerprints, provenance-backed malware signatures, and verifier routines.

## Tests

Host regression tests cover:

- checksum-valid DOS bootblock;
- corruption causing checksum failure;
- conservative `UNKNOWN` classification for invalid-checksum DOS data;
- synthetic signature detection;
- unknown custom data;
- malformed/short input.

Runtime requalification on Kickstart 1.2 is required after merge because scanner behavior has changed, although no new operating-system dependency is introduced.
