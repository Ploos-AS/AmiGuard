# M2.2m — neutral research-sample analysis

M2.2m adds a host-only offline analysis stage between M2.2l research intake and any future signature qualification.

## Safety boundary

`tools/analyze_research_sample.py` does not classify an input as malware and cannot activate a native AmiGuard signature. Every report states `malware_claim: false`, `native_activation: false`, and `classification: UNDETERMINED`.

The tool records SHA-256 and size, printable strings with offsets, 32-bit-aligned words that resemble known Amiga HUNK record identifiers, and a small set of neutral byte windows for human review. Candidate windows are observations, not signatures.

When `--intake` is supplied, the sample SHA-256 must match the M2.2l intake metadata before analysis proceeds. Symlinks and files above AmiGuard's 128 KiB file-intake limit are rejected.

## Promotion boundary

There is deliberately no promotion output. A future real-malware detection still requires lawful sample provenance, human analysis, sample-backed verification, clean-corpus qualification, explicit signature lifecycle gates, and native runtime qualification before AmiGuard may make an `INFECTED` claim.

This milestone can be qualified entirely with synthetic benign fixtures. No real malware is required and no sample bytes are committed to the repository.

## Example

```sh
python3 tools/analyze_research_sample.py sample.bin --intake intake.json -o analysis.json
```
