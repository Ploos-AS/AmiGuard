# M3.0 — disk scanner architecture

Status: IMPLEMENTED — qualification pending

M3 introduces AmiGuard's third explicit scanner engine: Disk. M3.0 defines the architecture only; recursive filesystem traversal, raw trackdisk inspection and ADF parsing are delivered by M3.1–M3.3.

## Design goals

The disk engine is read-only, bounded and compatible with the existing AmigaOS/Kickstart 1.2+, Motorola 68000 and low-memory design. It orchestrates existing detectors instead of duplicating file or bootblock signature logic.

The engine separates three source providers:

- mounted volume/directory provider;
- `trackdisk.device` raw-media provider;
- disk-image/ADF provider.

Providers expose logical objects to the core as files, bootblocks or raw regions. The provider API intentionally has no write callback.

## Detector reuse

Filesystem objects flow to the existing file scanner. Bootblocks flow to the existing bootblock scanner. Raw-region detection receives a dedicated qualified format only when M3 requires it; M3.0 does not silently reinterpret file signatures as arbitrary-sector signatures.

A disk-level `INFECTED` verdict may therefore only originate from an independently verified production detector. Safe/test detections and xvs detections retain their existing verdict separation.

## Bounded operation

Every scan configuration must bound object count, traversal depth and raw bytes inspected. `AMIGUARD_DISK_IO_BUFFER_BYTES` is 4096 bytes so future providers can stream objects through small caller-owned buffers rather than loading whole disks into RAM.

The statistics structure records objects, files, bootblocks, raw regions, bytes read and errors. Later milestones must preserve partial-scan/error reporting rather than treating unreadable media as clean.

## Provider lifecycle

`next_object()` selects the next logical object, `read_object()` streams bytes into caller-owned storage, and `close_object()` closes that logical object. The interface is intentionally minimal and C89/68000-friendly.

M3.1 implements mounted-volume traversal. M3.2 implements raw trackdisk media. M3.3 implements ADF/full-image scanning. M3.4 supplies final native runtime qualification.

## M3.0 completion gate

M3.0 passes when host CI compiles/tests the architecture and existing native/FS-UAE provisional qualification remains green. No authentic malware sample is required because architecture qualification uses clean and synthetic fixtures only.
