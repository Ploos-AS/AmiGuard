# M2.7 — ASW/AmiSandbox handoff contract

Status: IMPLEMENTED — qualification pending

M2.7 defines the machine-readable boundary between AmiGuard and analysis systems such as AmiGuard Signature Workstation (ASW) and AmiSandbox.

## Trust model

ASW and AmiSandbox are evidence producers, not signature authorities. A valid handoff may propose a candidate, but validation never activates a signature and never grants an `INFECTED` verdict.

Every production candidate still passes AmiGuard's independent review, clean-corpus differential qualification, qualified proposal, native runtime verification, verified finalization, activation review, generated-table consistency and CI gates.

## Handoff format

The contract identifier is `amiguard-asw-handoff-v1`. The normative JSON Schema is `schemas/asw-handoff-v1.schema.json`; `tools/validate_asw_handoff.py` provides the dependency-free repository validator used by AmiGuard tooling and tests.

A handoff binds evidence to an exact sample SHA-256 and size. Sample bytes are not part of the handoff and must not be committed merely to satisfy this contract. `redistributable` records whether the sample may legally be redistributed; it does not cause AmiGuard to redistribute it.

Supported sample kinds in v1 are `file`, `bootblock`, `disk-image`, and `memory-artifact`. Candidate byte signatures are currently accepted only for `file` and `bootblock`, matching the implemented AmiGuard production signature engines. Disk and memory analysis may be handed off as evidence before their future M3/M4 signature formats exist.

## Verdict discipline

`analysis.result` is one of `candidate`, `inconclusive`, or `clean`. A `candidate` requires a signature proposal. `clean` and `inconclusive` must not contain a signature proposal.

A candidate is explicitly untrusted. The validator checks structure, hash binding, kind consistency and bounded metadata semantics only. It does not prove malware identity, uniqueness, safety, false-positive resistance, runtime behavior, or provenance.

## Compatibility

The handoff is host-side JSON and does not change AmiGuard's Kickstart 1.2+, Motorola 68000 or low-memory native runtime requirements.

## M2.7 completion gate

M2.7 passes when host CI validates the contract tests and the existing FS-UAE/AROS provisional qualification remains green. No authentic malware sample is required for this engineering milestone; M2.5 remains parallel and sample-dependent.
