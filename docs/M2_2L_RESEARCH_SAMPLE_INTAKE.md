# M2.2l — Research sample intake

M2.2l adds a deliberately non-activating intake step for future historical
Amiga malware research artifacts. It is designed for the point where an
operator has obtained a sample through a lawful, controlled research source.
No sample is required to complete this host-side infrastructure milestone.

`tools/intake_research_sample.py` reads a local regular file, computes SHA-256
and size twice, and rejects the intake if the artifact changes while being
examined. An optional externally recorded SHA-256 can be required with
`--expected-sha256`.

The JSON output contains only metadata: basename, size, SHA-256, operator
supplied source/provenance and an optional neutral label. It never embeds or
copies sample bytes, records no absolute local path, defines no cleaner and
sets both `malware_claim` and `native_activation` to false. Symbolic links are
rejected.

Example for a future controlled artifact:

```sh
python3 tools/intake_research_sample.py /quarantine/candidate.bin \
  --source "operator-controlled research archive" \
  --provenance "acquisition notes and archive reference" \
  --expected-sha256 <independently-recorded-sha256> \
  --label "unverified historical candidate" \
  -o /tmp/candidate-intake.json
```

The output is research evidence only. It must not be interpreted as proof that
the artifact is malware, and it cannot promote or activate a native AmiGuard
signature. Sample-backed analysis, independent provenance review, clean-corpus
qualification and native runtime qualification remain later gates.

## Completion gate

M2.2l is complete when host tests and CI pass on the exact final commit. No
FS-UAE qualification is required because neither native AmiGuard code nor the
generated native signature tables change in this milestone.
