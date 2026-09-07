# M2.2n — candidate file-signature review gate

M2.2n adds an explicit human-review boundary after M2.2m neutral sample analysis.

`tools/review_file_signature_candidate.py` accepts an M2.2m analysis report plus one exact byte window already observed by that report. A reviewer must provide a non-empty identity and rationale. The output is a separate research artifact with kind `amiguard-file-signature-candidate-review` and status `research-candidate`.

## Safety contract

A review output is **not** a compiled AmiGuard signature and cannot activate native detection. It always records:

- `candidate_is_verified_signature: false`
- `malware_claim: false`
- `native_activation: false`
- `promotion: null`
- `cleaner: null`

The tool rejects analyses that violate the M2.2m neutral contract, invalid sample hashes, malformed candidate windows, and any byte sequence that does not exactly match an M2.2m observed candidate window.

Human approval here means only "worth further research". It does not mean the sample is malware and does not permit an `INFECTED` verdict.

## Required later gates

Before any candidate can become a real detection it still requires sample-backed verification, clean-corpus regression, a separate lifecycle promotion step, and visible native Amiga runtime qualification.

No malware samples are needed to qualify M2.2n; repository tests use synthetic benign metadata. M2.2n changes host-side research tooling only, so no new FS-UAE runtime qualification is required.

## Example

```sh
python3 tools/review_file_signature_candidate.py analysis.json \
  --offset 32 \
  --hex 0123456789abcdef0123456789abcdef \
  --reviewer "researcher-name" \
  --rationale "candidate code window selected for differential review" \
  -o candidate-review.json
```

Do not commit live malware bytes to the public repository. Candidate review artifacts should be sanitized research evidence only.
