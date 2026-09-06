# M1.2e — Verified promotion tooling

## Goal

Provide one local command that turns a qualified bootblock-signature candidate into a `verified` AmiGuard metadata draft only after the positive sample and clean-corpus gates pass.

The tool does not edit repository metadata, does not commit anything, and does not copy malware samples into the repository. The generated draft contains only the sample bootblock SHA-256, provenance summary, and the explicitly supplied signature offset/pattern/mask.

## Workflow

1. Build or refresh a local clean-media manifest:

```sh
python3 tools/build_clean_manifest.py /clean/wb12.adf /clean/wb13.adf -o /tmp/amiguard-clean.json
```

2. Analyze the isolated sample and choose a candidate offset/pattern/mask through independent research:

```sh
python3 tools/analyze_bootblock.py /isolated/sample.adf --json
```

3. Run the qualification gate directly when investigating candidates:

```sh
python3 tools/qualify_signature.py \
  /isolated/sample.adf \
  --clean-manifest /tmp/amiguard-clean.json \
  --offset 64 \
  --pattern 00112233 \
  --mask ffffffff
```

4. Once the candidate passes, generate a verified metadata draft:

```sh
python3 tools/promote_signature.py \
  /isolated/sample.adf \
  --clean-manifest /tmp/amiguard-clean.json \
  --offset 64 \
  --pattern 00112233 \
  --mask ffffffff \
  --id family.variant \
  --name "Family Variant" \
  --family Family \
  --source "documented research source" \
  --provenance-note "Signature independently derived from isolated sample and clean regression" \
  -o /tmp/family-variant.verified.json
```

The promotion command exits non-zero and emits no verified draft when the candidate does not match the isolated sample, when any clean entry matches, when a clean manifest hash has changed, or when the manifest/input is malformed.

## Required human review before repository inclusion

A generated `verified` draft is evidence packaging, not automatic approval. Before copying it under `signatures/bootblocks/`, review that:

- the sample source/provenance is legally and technically acceptable;
- the SHA-256 corresponds to the analyzed bootblock;
- the offset/pattern/mask was independently derived rather than copied from an unlicensed third-party database;
- the pattern is sufficiently discriminating and stable for the intended family/variant;
- the clean corpus is representative enough for the claimed detection;
- variant coverage claims are limited to what has actually been tested;
- cleaner support remains `none` unless separately implemented and qualified.

After review, place the metadata in the repository, run `make signatures && make check`, and then perform native Kickstart 1.2 runtime qualification before calling the first real detection complete.

## Acceptance criteria

- promotion reuses the same positive/negative qualification gate as M1.2c;
- failed qualification cannot create `verified` metadata;
- passing qualification produces schema-1 metadata accepted by the M1.1 compiler;
- sample bytes are never embedded beyond the explicitly chosen signature bytes/mask;
- no sample or clean-media file is committed by the tool;
- promotion tests are part of `make check`;
- no Amiga runtime dependency changes are introduced.
