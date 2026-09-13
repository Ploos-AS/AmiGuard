# AmiGuard roadmap

AmiGuard develops a standalone antivirus engine for classic Amiga systems while keeping the AmigaOS/Kickstart 1.2+, Motorola 68000 and low-memory runtime targets.

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

### M2.4 — verified file-signature finalization — ACTIVE

Bind a qualified file-signature proposal to exact visible native runtime evidence before it can become `verified`. The finalization tool is deliberately side-effect-free; activation remains a separately reviewed repository change followed by generated-table, host and native qualification.

See `docs/M2_4_VERIFIED_FILE_SIGNATURE_FINALIZATION.md`.

## Next milestones

### M2.5 — first production malware signature

Use an authentic, lawfully obtained research sample to exercise the complete pipeline: intake → analysis → candidate → review → differential clean-corpus qualification → qualified proposal → native runtime PASS → verified signature → activation. No malware sample bytes are committed to the public repository.

### M2.6 — production signature database operations

Introduce database/version metadata, reproducible signature-set manifests, release-time production-signature inventory, deterministic database identity and update-policy documentation.

### M2.7 — ASW handoff contract

Define the machine-readable exchange contract between AmiGuard and AmiGuard Signature Workstation/AmiSandbox for candidate evidence and analysis artifacts. ASW may propose evidence and candidates but cannot bypass AmiGuard review, clean-corpus qualification or native finalization gates.

## Release discipline

Every release must retain green host CI, generated-signature consistency, packaging verification and required visible native qualification. Test/safe-test detections must never silently become production `INFECTED` detections, and external xvs detections remain `XVS-DETECTED` until independently verified by AmiGuard.
