# M2.2p — qualified candidate proposal gate

M2.2p introduces the first explicit transition from a reviewed research candidate plus passing differential evidence into a compiler-compatible `qualified` file-signature proposal.

The gate consumes:

- an M2.2n `amiguard-file-signature-candidate-review` artifact; and
- an M2.2o `amiguard-file-signature-candidate-qualification` report.

It requires exact sample SHA-256 and size agreement between those artifacts, a positive candidate match, at least one clean file tested, zero clean-corpus collisions, and a passing differential qualification.

## Safety boundary

A generated proposal has `status: qualified`, but the file-signature compiler does **not** render `qualified` records into the native signature table. Only `verified` malware signatures are active in native `INFECTED` detection.

Every M2.2p output therefore records:

- `candidate_is_verified_signature: false`
- `malware_claim: false`
- `native_activation: false`
- `requires_visible_native_runtime: true`
- `cleaner: none`

M2.2p cannot by itself create a verified signature or an `INFECTED` verdict.

## Usage

```sh
python3 tools/promote_qualified_file_signature.py \
  candidate-review.json candidate-qualification.json \
  --id example-family \
  --name "Example family" \
  --family "Example" \
  --source "lawfully acquired research sample" \
  --provenance "operator-reviewed provenance notes" \
  --verifier "sample-backed verifier description" \
  -o qualified-proposal.json
```

The proposal may then be validated with `tools/compile_file_signatures.py` after placing a reviewed copy in `signatures/files/`; because its status is `qualified`, that validation must not change `src/file_signatures_generated.inc`.

## Later gate

A future milestone must bind the qualified proposal to visible native Amiga runtime evidence before any transition to `verified`. That later step is intentionally separate and must not be bypassed.

M2.2p is host-only. Repository CI with synthetic fixtures is sufficient for this milestone; no FS-UAE run is required until native behavior or activation changes.
