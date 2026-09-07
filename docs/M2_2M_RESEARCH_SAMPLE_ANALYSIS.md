# M2.2m — neutral research-sample analysis

M2.2m adds a host-only offline analysis stage between M2.2l research intake and any future signature qualification.

## Safety boundary

`tools/analyze_research_sample.py` does not classify an input as malware and cannot activate a native AmiGuard signature. Every report states `malware_claim: false`, `native_activation: false`, and `classification: UNDETERMINED`.

The tool records SHA-256 and size, printable strings with offsets, 32-bit-aligned words that resemble known Amiga HUNK record identifiers, and a small set of neutral byte windows for human review. Candidate windows are observations, not signatures. HUNK record candidates are lexical 32-bit observations, not proof that the input is a structurally valid HUNK executable; native structural parsing remains a separate concern.

When `--intake` is supplied, the sample SHA-256 must match the M2.2l intake metadata before analysis proceeds. Symlinks and files above AmiGuard's 128 KiB file-intake limit are rejected. The tool records file identity/size/mtime before and after its read and aborts if the sample changes during analysis.

## Promotion boundary

There is deliberately no promotion output. A future real-malware detection still requires lawful sample provenance, human analysis, sample-backed verification, clean-corpus qualification, explicit signature lifecycle gates, and native runtime qualification before AmiGuard may make an `INFECTED` claim.

This milestone can be qualified entirely with synthetic benign fixtures. No real malware is required and no sample bytes are committed to the repository. Because M2.2m changes host-only research tooling and does not alter generated signature tables or native C code, visible FS-UAE qualification is not required for this milestone.

## Qualification

M2.2m is complete when repository CI passes with tests covering neutral report generation, matching and mismatching M2.2l intake linkage, wrong intake kind, symlink and oversize rejection, JSON output-file generation, and short-input neutrality. The report contract must continue to assert no malware claim, no native activation, no cleaner, and no promotion.

## Example

```sh
python3 tools/analyze_research_sample.py sample.bin --intake intake.json -o analysis.json
```

The generated analysis JSON is research evidence. Do not place real sample bytes in the repository; only sanitized metadata/evidence may be reviewed for a future signature milestone.

## Status

Implemented on `main`. Completion is determined by the qualification contract above and CI on the final milestone commit; it does not imply that AmiGuard has acquired or detected any real Amiga malware.

No native signature tables, file scanner verdicts, or bootblock scanner behavior are changed by M2.2m.
