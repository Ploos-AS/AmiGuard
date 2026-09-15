# M4.0 — Memory scanner architecture

Status: **IMPLEMENTED — qualification pending**

M4 introduces AmiGuard's fourth scanner engine: live-memory inspection for classic Amiga systems.

## Design goals

The memory engine must remain usable on the existing AmiGuard baseline: AmigaOS/Kickstart 1.2+, Motorola 68000 and low-memory machines. Scanning is read-only. Detection must never implicitly patch vectors, remove residents, kill tasks, close libraries/devices, quarantine RAM or otherwise alter the inspected machine.

## Provider boundary

`src/memory_scanner.h` defines a provider with only three operations:

- enumerate the next inspectable object;
- copy a bounded range from that object into caller-owned memory;
- optionally close provider state.

There is deliberately no write callback.

M4.1 providers will expose OS-visible residents, tasks/processes, libraries and devices. M4.2 will add explicitly selected vector/hook objects. M4.3 will add eligible bounded RAM regions.

## Object classes

The core distinguishes:

- resident modules;
- tasks/processes;
- libraries;
- devices;
- vectors/hooks;
- bounded raw memory regions.

Keeping the classes explicit lets qualification and signature provenance state exactly what was inspected.

## Bounds

Every scan is constrained by:

- maximum object count;
- maximum aggregate bytes read;
- maximum bytes accepted for one region.

The streaming buffer target is 1024 bytes. Providers must copy memory into scanner-owned buffers; detector code must not depend on arbitrary direct pointer walks across unbounded RAM.

Invalid/null addresses, zero-sized objects, unknown object classes and objects larger than the configured per-region limit are rejected.

## Verdicts

The memory layer reserves separate verdicts for clean, safe/test signature, production infected, suspicious and error states. A suspicious structural condition is not equivalent to a verified malware signature. Safe/test evidence must never be promoted into production `INFECTED` merely because it was observed in RAM.

## AmigaOS safety model

M4.1 must enumerate OS structures using the narrowest practical Exec-visible interfaces/structures for the supported Kickstart range. Because live lists can change while multitasking is active, providers should snapshot only the minimal metadata needed and avoid holding system-wide exclusion longer than necessary. The scanner must not retain pointers and later assume they remain valid without provider-controlled validation/copying.

For the 1.2+ compatibility target, implementation must not depend on APIs introduced only in later AmigaOS releases unless guarded by a compatible fallback.

## Milestone split

- **M4.0:** architecture, object model, bounds and read-only contract.
- **M4.1:** resident/task/library/device enumeration.
- **M4.2:** selected vectors/hooks integrity inspection.
- **M4.3:** bounded RAM signature scanning.
- **M4.4:** native/visible runtime qualification and clean/safe-test corpus.

Production malware qualification remains subject to the same independent evidence and activation discipline used by AmiGuard's file and bootblock engines.
