# AmiGuard roadmap

AmiGuard develops a standalone antivirus engine for classic Amiga systems while keeping the AmigaOS/Kickstart 1.2+, Motorola 68000 and low-memory runtime targets.

The long-term scanner architecture has four explicit engines: **File**, **Bootblock**, **Disk** and **Memory**. File, bootblock and disk scanning are established; live-memory scanning is the current engineering track and is required before AmiGuard is considered feature-complete as a classic Amiga antivirus.

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

### M2.0–M2.4 — file scanning, research and finalization pipeline — DONE

HUNK parsing, bounded file intake, file-signature framework, safe-test lifecycle, ADF clean corpus, research sample intake/analysis, candidate review and differential qualification, qualified candidate proposals, optional xvs bridge, and verified file-signature finalization bound to exact native runtime evidence.

### M2.6 — production signature database operations — DONE

Database/version metadata, reproducible signature-set manifest, deterministic database identity, production inventory and CI consistency gating. M2.6 completed with green host CI and FS-UAE/AROS provisional qualification.

### M2.7 — ASW handoff contract — DONE

Machine-readable ASW/AmiSandbox handoff contract with sample hash binding, candidate validation and an explicit trust boundary. Host CI and FS-UAE/AROS provisional qualification passed on M2.7.

### M3.0–M3.3 — disk engine implementation — DONE

Read-only disk/volume architecture, recursive mounted-volume scanning, bounded raw `trackdisk.device` access and ADF/full-image scanning. The disk engine reuses established file and bootblock detector authorities and exposes no write/repair path.

### M3.4 — disk runtime qualification — DONE / PASS

The consolidated disk qualification gate passed for recursive volume, raw floppy/media and ADF image paths. FS-UAE/AROS provisional qualification run #69 / ID `35008535211` completed successfully, including host regressions, native Bebbo/68000 build, guest detector execution, M3.4 consolidated disk qualification and evidence upload.

The **Disk** engine is therefore closed as qualified engineering scope. Visible classic-Amiga evidence remains part of release/historical compatibility discipline where required.

### M4.0 — memory scanner architecture — DONE / PASS

The read-only bounded memory-inspection contract is established for resident, task, library, device, vector/hook and raw-region objects. Object, aggregate-byte and per-region limits are explicit; the provider contract has no write callback. The native 68000 build and existing runtime gates remained green when the first Exec provider was integrated (FS-UAE/AROS provisional qualification run #80 / ID `35024520694`).

See `docs/M4_0_MEMORY_SCANNER_ARCHITECTURE.md`.

## Parallel sample-dependent milestone

### M2.5 — first production malware signature — WAITING FOR AUTHENTIC SAMPLE

Use an authentic, lawfully obtained research sample to exercise the complete pipeline: intake → analysis → candidate → review → differential clean-corpus qualification → qualified proposal → native runtime PASS → verified signature → activation. No malware sample bytes are committed to the public repository. M2.5 does not block engineering milestones while AmiGuard waits for a suitable submitted sample.

## Current engineering milestone

### M4.1 — resident/task/library/device inspection — ACTIVE

Enumerate relevant resident modules, tasks/processes, libraries and devices through a bounded read-only Exec provider and report inspectable objects without modifying system state. The initial provider, host tests and native integration are green; M4.1 remains active until the supported object classes and runtime evidence are complete.

## M4 — live-memory scanning

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
