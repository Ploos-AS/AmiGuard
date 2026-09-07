# M2.2o — differential candidate qualification

M2.2o tests an M2.2n human-reviewed research candidate against its exact positive sample and a trusted clean-file corpus.

`tools/qualify_file_signature_candidate.py` binds the candidate to the sample SHA-256 and size recorded by M2.2n, confirms the masked candidate matches that positive artifact, and rejects candidates that collide with any supplied clean file. Clean inputs may be supplied directly or through an `amiguard-clean-file-corpus` manifest; manifest file size and SHA-256 are revalidated before use.

## Safety contract

A passing M2.2o report is still **not a verified malware signature**. It always records:

- `candidate_is_verified_signature: false`
- `promotion_ready: false`
- `malware_claim: false`
- `native_activation: false`
- `cleaner: null`

A pass means only that this particular reviewed byte pattern matches the bound positive artifact and did not match the supplied clean corpus. It does not prove malware identity, uniqueness across all legitimate Amiga software, or permission to return `INFECTED`.

The tool exits 0 for a differential pass, 1 for a valid but failing candidate (positive mismatch or clean collision), and 2 for malformed or inconsistent evidence.

## Qualification

Repository CI uses harmless synthetic fixtures and must cover a clean differential pass, a clean-corpus collision, positive-sample hash binding, manifest revalidation, and rejection of a non-neutral M2.2n review.

M2.2o is host-only. It changes no native code and no generated signature table, so visible FS-UAE qualification is not required.

When a lawful real sample becomes available, the same gate can be run against the operator-selected 963-file Amiga Forever clean corpus already produced by the M2.2i workflow. A later separate lifecycle gate must still decide whether sufficient evidence exists to create a qualified signature proposal, followed by visible native runtime qualification before any verified activation.
