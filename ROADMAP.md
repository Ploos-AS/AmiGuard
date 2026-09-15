# AmiGuard roadmap

AmiGuard develops a standalone antivirus engine for classic Amiga systems while keeping the AmigaOS/Kickstart 1.2+, Motorola 68000 and low-memory runtime targets.

The long-term scanner architecture has four explicit engines: **File**, **Bootblock**, **Disk** and **Memory**. File and bootblock scanning are already established; full-disk and live-memory scanning are planned below and are required before AmiGuard is considered feature-complete as a classic Amiga antivirus.

## Released baseline

### v0.1.0 — first public release — DONE

- bootblock and file scanning foundations;
- independently controlled signature metadata and generated native tables;
- safe/test signature paths kept separate from production malware verdicts;
- optional transitional `xvs.library` bridge with `XVS-DETECTED` verdict separation;
- visible classic-Amiga qualification and automated GitHub release packaging.

## Completed engineering milestones

### M1 — bootblock signature lifecycle — DONE

Schema, research gate, qualification, clean-corpus controls, promotion tooling, provenance/review lifecycle, triage and known-clean lifecycle.

### M2.0–M2.3 — file scanning and research pipeline — DONE

HUNK parsing, bounded file intake, file-signature framework, safe-test lifecycle, ADF clean corpus, research sample intake/analysis, candidate review and differential qualification, qualified candidate proposals, and the optional xvs bridge.

## Current milestone

### M2.4 — verified file-signature finalization — DONE

Bind a qualified file-signature proposal to exact visible native runtime evidence before it can become `verified`. The finalization tool is deliberately side-effect-free; activation remains a separately reviewed repository change followed by generated-table, host and native qualification.

See `docs/M2_4_VERIFIED_FILE_SIGNATURE_FINALIZATION.md`.

## Next milestones

### M2.5 — first production malware signature

Use an authentic, lawfully obtained research sample to exercise the complete pipeline: intake → analysis → candidate → review → differential clean-corpus qualification → qualified proposal → native runtime PASS → verified signature → activation. No malware sample bytes are committed to the public repository.

### M2.6 — production signature database operations

Introduce database/version metadata, reproducible signature-set manifests, release-time production-signature inventory, deterministic database identity and update-policy documentation.

### M2.7 — ASW handoff contract

Define the machine-readable exchange contract between AmiGuard and AmiGuard Signature Workstation/AmiSandbox for candidate evidence and analysis artifacts. ASW may propose evidence and candidates but cannot bypass AmiGuard review, clean-corpus qualification or native finalization gates.

## M3 — full-disk scanning

### M3.0 — disk scanner architecture

Define a read-only disk/volume scanning API that remains compatible with Kickstart 1.2+, 68000 and low-memory systems. Separate filesystem traversal from raw-media inspection so the same detector core can be reused safely.

### M3.1 — recursive volume/file scan

Scan files throughout a selected mounted volume or directory tree using the existing file engine, with bounded buffers, deterministic traversal and clear per-object verdicts.

### M3.2 — raw floppy/media inspection

Add read-only raw disk inspection through trackdisk-compatible interfaces. Inspect the bootblock plus relevant raw sectors/blocks that filesystem-only traversal cannot cover. Never write, repair or disinfect media in the scanning path.

### M3.3 — ADF/full-disk image scan

Scan complete disk images using the same disk engine where practical, including bootblock, filesystem-visible files and raw regions. Add clean and safe-test disk-image qualification corpora.

### M3.4 — disk runtime qualification

Qualify volume, floppy and disk-image scanning on native m68k builds and visible Amiga runtime evidence, including low-memory operation and malformed-media handling.

## M4 — live-memory scanning

### M4.0 — memory scanner architecture

Define a read-only, bounded memory-inspection engine suitable for classic AmigaOS. Document which memory regions and OS structures may be inspected safely on supported Kickstart versions.

### M4.1 — resident/task/library/device inspection

Enumerate relevant resident modules, tasks/processes, libraries and devices and report suspicious or signature-matching objects without modifying system state.

### M4.2 — vectors and hooks integrity

Inspect selected Exec/OS vectors, interrupt/server structures and other historically relevant hooks for known malicious modifications or qualified heuristics while controlling false positives across supported Kickstart versions.

### M4.3 — RAM signature scanning

Add bounded signature matching over eligible RAM regions with strict limits appropriate for 68000 and 512 KiB-class machines. Reuse verified signature metadata where semantically valid and keep memory-specific signatures explicit where needed.

### M4.4 — memory runtime qualification

Qualify memory scanning against clean systems and controlled safe-test fixtures on native m68k/visible Amiga runtime. Production malware verdicts require the same independent evidence and review discipline as file and bootblock signatures.

## Feature-complete scanner target

AmiGuard's scanner is considered feature-complete only when all four engines are qualified:

1. **File** — individual executable/data file scanning.
2. **Bootblock** — bootblock classification and signature scanning.
3. **Disk** — recursive filesystem plus relevant raw-media/full-image inspection.
4. **Memory** — live resident/object/vector/RAM inspection.

All engines are read-only by default. Detection, quarantine, repair and disinfection are separate concerns and must never be implicit side effects of scanning.

## Release discipline

Every release must retain green host CI, generated-signature consistency, packaging verification and required visible native qualification. Test/safe-test detections must never silently become production `INFECTED` detections, and external xvs detections remain `XVS-DETECTED` until independently verified by AmiGuard.
