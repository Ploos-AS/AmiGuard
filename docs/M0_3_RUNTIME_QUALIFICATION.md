# M0.3 Runtime Qualification

## Purpose

Qualify the AmiGuard native binary on an Amiga 500-class runtime with
Motorola 68000 and Kickstart/Workbench 1.2.

This is a visible runtime gate. Host CI alone does not satisfy M0.3.

## Required machine profile

- Amiga 500
- Motorola 68000
- Kickstart 1.2
- 512 KiB Chip RAM minimum target
- no accelerator/JIT requirement
- visible FS-UAE session or equivalent real hardware

## Preconditions

1. Build AmiGuard with a m68k-amigaos compiler and `-m68000`.
2. Copy `AmiGuard` to a writable Amiga volume available to the test machine.
3. Boot a clean Kickstart/Workbench 1.2 environment.
4. Insert a known-clean DOS-formatted floppy image in DF0:.

## Gate A — process startup

Run:

    AmiGuard

Expected:

- program starts without Guru Meditation,
- usage/help text is printed,
- process exits normally,
- no OS 2.x-only dependency failure appears.

Result: UNVERIFIED

## Gate B — DF0 bootblock read

Run:

    AmiGuard DF0:

Expected:

- exactly the first 1024 bytes are read through `trackdisk.device`,
- scan completes without modifying the disk,
- the result is reported as known DOS bootblock, unknown/custom, or infected,
- program exits normally.

Result: UNVERIFIED

## Gate C — invalid target handling

Run representative invalid inputs:

    AmiGuard DH0:
    AmiGuard DF4:

Expected:

- inputs are rejected,
- no device write is attempted,
- process exits cleanly.

Result: UNVERIFIED

## Gate D — missing/no media handling

Run with DF0: empty:

    AmiGuard DF0:

Expected:

- read failure is reported clearly,
- no crash or hang,
- process exits cleanly.

Result: UNVERIFIED

## Gate E — repeated read stability

Repeat:

    AmiGuard DF0:

at least 10 times against the same clean image.

Expected:

- identical classification each time,
- no resource leak visible through progressive failures,
- no crash or stale-device behavior.

Result: UNVERIFIED

## Gate F — 512 KiB target

Repeat Gates A and B using a 512 KiB A500 configuration if practical.

Expected:

- AmiGuard starts and completes a single DF0: bootblock scan.

If this does not fit, record the measured minimum memory instead of silently
raising the requirement.

Result: UNVERIFIED

## Evidence to record

For each gate record:

- exact AmiGuard commit SHA,
- compiler/toolchain identity,
- resulting binary size,
- FS-UAE version,
- machine profile,
- Kickstart version/hash if available,
- floppy image description and hash where redistribution permits,
- command used,
- observed output,
- PASS/FAIL.

## Completion rule

M0.3 is complete only after Gates A-E pass on Kickstart 1.2 / 68000.
Gate F determines whether the 512 KiB minimum target is confirmed or must be
revised with measured evidence.
