# M2.0 — HUNK parser foundation

## Goal

Establish a small, native C89 parser for Amiga executable HUNK structure before adding any file-virus signatures or remediation.

## Classification

The parser returns only structural results:

- `AMIGUARD_HUNK_NOT_HUNK` — input does not begin with a HUNK header.
- `AMIGUARD_HUNK_VALID` — supported HUNK structure parsed completely and consistently.
- `AMIGUARD_HUNK_MALFORMED` — input claims to be HUNK but is truncated, inconsistent, unsupported, or contains trailing data.

These are file-format results only. None of them are malware claims.

## Scope

M2.0 parses the executable HUNK header, hunk-size table, CODE, DATA, BSS, RELOC32, SYMBOL, DEBUG and END records with strict bounds checks. Unsupported record types fail closed as `MALFORMED` for this milestone rather than being silently skipped.

The parser is C89-compatible and included in the native 68000 build. Host regression tests exercise valid, non-HUNK, truncated and trailing-data cases.

## Safety

M2.0 is read-only. It does not open files itself, modify data, emit signatures, classify malware, or clean anything.

## Qualification

`make check` must compile and run the dedicated host HUNK parser test alongside the existing bootblock and lifecycle tests. Because the parser is now linked into the native executable, a visible AmigaOS 1.2 runtime requalification is required before M2.0 is considered fully complete.
