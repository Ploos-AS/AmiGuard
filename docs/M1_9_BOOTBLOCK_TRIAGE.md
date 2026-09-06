# M1.9 — Bootblock triage reporting

M1.9 strengthens the host-side bootblock research analyzer without changing the native Amiga scanner.

## Scope

`tools/analyze_bootblock.py` remains read-only and analyzes only the first 1024 bytes as the bootblock. It now emits structural triage fields that mirror the native scanner's non-malware classification semantics:

| Structural state | classification | reason_code |
| --- | --- | --- |
| DOS0-DOS7 + valid checksum | `STANDARD` | `dos-valid-checksum` |
| DOS0-DOS7 + invalid checksum | `UNKNOWN` | `dos-invalid-checksum` |
| non-DOS + valid checksum | `CUSTOM` | `non-dos-valid-checksum` |
| non-DOS + invalid checksum | `UNKNOWN` | `non-dos-invalid-checksum` |

The report also includes `malware_claim: false`.

## Safety semantics

These classifications are structural triage only.

- `STANDARD` does not mean malware-free.
- `CUSTOM` is neutral and does not imply maliciousness.
- `UNKNOWN` does not mean infected.
- `INFECTED` remains reserved for a compiled, verified malware signature in the native scanner.
- No host-side heuristic may promote an item to malware solely from DOS type, checksum state, strings, or custom structure.

This distinction is intentional because AmiGuard does not yet have a verified historical malware sample in the repository workflow.

## Machine-readable output

`--json` now includes:

- `classification`
- `reason_code`
- `malware_claim`
- existing SHA-256, DOS type, checksum and printable-string evidence

The stable reason codes are intended for later corpus triage, reporting and tooling without parsing human-readable text.

## Acceptance gates

M1.9 requires host tests proving all four structural classifications, including a valid non-DOS custom bootblock, and proving that structural analysis never asserts a malware claim.

`make check` and GitHub Actions CI must remain green.

## Runtime qualification

No visible FS-UAE runtime requalification is required for M1.9 because no native C source, generated signature table or Amiga executable behavior changes in this milestone.
