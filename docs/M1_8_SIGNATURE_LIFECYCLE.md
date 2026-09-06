# M1.8 — Signature lifecycle consistency

## Purpose

Prevent a host-qualified malware signature from being treated as native-runtime
verified before visible minimum-platform qualification has actually happened.

## Lifecycle

AmiGuard malware signature metadata now uses four states:

1. `test-only` — synthetic repository test signature; compiled only for tests/current native table behavior.
2. `research` — non-synthetic research record with provenance but no production signature and no claimed `sample_sha256`.
3. `qualified` — exact sample hash plus concrete signature that passed host positive-match and clean-corpus regression gates. It is **not compiled** into the native signature table.
4. `verified` — a qualified signature with explicit native runtime PASS evidence. Only this non-synthetic state is compiled into the native signature table.

`INFECTED` therefore remains reserved for compiled signatures, and a real malware
record cannot become compiled merely because host-side qualification passed.

## Tool flow

### Research

`tools/analyze_bootblock.py --draft` emits `status=research` and keeps
`sample_sha256=null`. Observed hashes remain in provenance so evidence is not lost.
This makes analyzer output consistent with the compiler's research schema.

### Host qualification

`tools/promote_signature.py` runs the qualification gate and emits
`status=qualified`, not `verified`.

`tools/preflight_signature.py` requires a qualified draft, validates it with the
compiler schema, rejects duplicate IDs, proves that the qualified record is not
rendered into the native table, and separately proves that its future verified
form can be rendered.

### Native runtime finalization

`tools/finalize_signature.py` requires:

- a `status=qualified` metadata draft;
- a JSON runtime evidence record with `result=pass`;
- non-empty `platform`, `os`, `cpu`, and `evidence` fields.

It emits a `status=verified` draft and embeds the runtime evidence under
`provenance.runtime_verification`. It does not modify repository files.

A real signature should only be committed as `verified` after visible native
qualification on the supported minimum runtime relevant to the detection path.
For the current bootblock scanner, the baseline remains visible A500 / Motorola
68000 / Kickstart 1.2 qualification.

## Compiler behavior

`tools/compile_signatures.py` accepts `test-only`, `research`, `qualified`, and
`verified`, but renders only `test-only` and `verified` records into
`src/signatures_generated.inc`.

This is the central M1.8 safety invariant:

> `qualified` means host-qualified, not native-runtime verified, and therefore is not compiled.

## Tests

Host tests cover:

- promotion produces `qualified`;
- failed qualification cannot promote;
- preflight requires `qualified`;
- qualified records do not render into the native table;
- the hypothetical verified form does render;
- finalization rejects non-qualified input;
- finalization rejects failed/incomplete runtime evidence;
- successful runtime evidence produces `verified` while preserving hash/signature fields;
- analyzer research drafts keep `sample_sha256=null` while retaining observed hashes in provenance.

## Runtime impact

M1.8 changes host-side metadata lifecycle and generation tooling only. It does not
change the current native scanner, trackdisk access, classification logic, or the
currently generated signature table. Therefore no new FS-UAE runtime
requalification is required solely for M1.8.
