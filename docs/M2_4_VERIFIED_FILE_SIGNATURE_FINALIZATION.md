# M2.4 — verified file-signature finalization

M2.4 closes the deliberate gap left by M2.2p: a compiler-compatible file signature may become `qualified` after research review and differential clean-corpus qualification, but it must not become an active AmiGuard malware signature until visible native runtime evidence is bound to that exact proposal.

## Gate

`tools/finalize_file_signature.py` accepts:

1. one `status: qualified`, `kind: file` proposal; and
2. one native runtime evidence JSON record.

The evidence must explicitly contain:

- `result: pass`
- the exact `signature_id`
- the exact `sample_sha256`
- non-empty `platform`, `os`, `cpu`, and `evidence` fields

The signature id and sample hash must match the qualified proposal. A failed, unrelated, synthetic, or unbound runtime record cannot promote the proposal.

## Safety boundary

The finalizer is side-effect-free. It emits a `status: verified` JSON draft but never writes into `signatures/files/` and never regenerates `src/file_signatures_generated.inc` automatically.

Activation therefore remains an explicit reviewed repository change:

1. preserve the qualification and native-runtime evidence;
2. run the M2.4 finalizer;
3. review the resulting verified JSON;
4. place the reviewed record in `signatures/files/`;
5. run `python3 tools/compile_file_signatures.py --write`;
6. run the complete host regression suite;
7. run visible native qualification again for the resulting build before release certification.

Only `verified` non-synthetic malware signatures are production `INFECTED` detections. `test-only` and `safe-test` records remain visibly test detections, and `qualified` records remain inactive.

## Acceptance criteria

- qualified file-signature input validates against the file-signature compiler schema;
- native evidence is bound to exact signature id and sample SHA-256;
- non-PASS native evidence is rejected;
- mismatched evidence is rejected;
- output validates as a `verified` file signature;
- proposal-only neutral flags are removed from the verified draft;
- host regression suite includes the finalizer tests;
- no production signature is added merely by completing M2.4.

M2.4 is the operational gate required before AmiGuard can safely accept its first independently verified production file-malware signature.
