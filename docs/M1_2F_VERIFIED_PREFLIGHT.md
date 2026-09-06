# M1.2f — Verified signature preflight

## Goal

Validate a generated `verified` metadata draft against the exact AmiGuard signature schema and native table renderer before the draft is copied into `signatures/bootblocks/`.

The preflight is side-effect free:

- it does not modify the draft;
- it does not copy the draft into the repository signature directory;
- it does not regenerate `src/signatures_generated.inc`;
- it does not read or copy additional malware bytes;
- it rejects non-`verified` records and duplicate signature IDs.

## Workflow

After M1.2e produces a verified draft:

```text
python3 tools/preflight_signature.py /isolated/work/mount-eleni-2.2.verified.json
```

A successful result reports `preflight_pass: true` together with the draft ID, sample SHA-256, current/combined metadata counts, and the size of the in-memory rendered native table.

Only after this preflight passes should a human review provenance, copy the metadata JSON into `signatures/bootblocks/`, run:

```text
python3 tools/compile_signatures.py --write
make check
```

and then perform native build plus visible Kickstart 1.2 runtime qualification.

## Gate

M1.2f does not make a signature trusted by itself. Promotion still requires the M1.2c positive/negative qualification evidence and M1.2e verified draft. M1.2f only proves that the proposed record is structurally acceptable to the production compiler and can be rendered with the existing metadata set without mutating the repository.
