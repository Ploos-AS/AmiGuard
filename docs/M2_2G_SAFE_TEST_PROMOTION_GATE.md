# M2.2g — Safe-test promotion gate

## Goal

Require concrete acquisition evidence before an external harmless antivirus test artifact can move from `research` to `safe-test`.

This milestone adds a side-effect-free promotion tool only. It does **not** promote the repository EICAR record yet, does not regenerate the native table, and does not change runtime behavior.

## Promotion tool

`tools/promote_safe_test.py` consumes:

1. a `status=research` file-signature metadata record;
2. a PASS acquisition report from the safe-test acquisition gate;
3. the exact locally acquired artifact.

The tool verifies that:

- the research record is non-synthetic and `kind=file`;
- acquisition schema/kind/id match the research record;
- `exact_standard_file=true`;
- `malware_claim=false`;
- `native_activation=false`;
- local artifact size and SHA-256 exactly match the acquisition report;
- the artifact is non-empty and within the 128 KiB file intake limit.

Only then does it emit a JSON proposal with:

- `status=safe-test`;
- exact artifact SHA-256 in `sample_sha256`;
- a concrete exact full-file signature at offset 0;
- an all-`ff` mask;
- `cleaner=none`;
- explicit `native_verdict=TEST-SIGNATURE`;
- explicit `malware_claim=false`;
- flags stating that clean-corpus preflight and visible native runtime qualification are still required.

The proposal is not written into `signatures/files/` automatically.

## Why exact full-file matching first

For a harmless interoperability artifact such as the canonical 68-byte EICAR file, the first activation candidate should be deliberately conservative. Matching the complete file at offset 0 minimizes false-positive risk and avoids deriving a weaker substring merely for convenience.

A shorter or masked signature may be considered later only with separate false-positive evidence.

## Example workflow

```sh
python3 tools/qualify_eicar_acquisition.py \
  /local/eicar.com.txt \
  --source-url <actual-authoritative-download-url> \
  --retrieved-at 2026-09-07 \
  --json > /tmp/eicar-acquisition.json

python3 tools/promote_safe_test.py \
  signatures/files/eicar-standard-av-test-research.json \
  /tmp/eicar-acquisition.json \
  /local/eicar.com.txt \
  -o /tmp/eicar-safe-test-proposal.json
```

The third-party artifact and temporary evidence files remain local unless explicitly reviewed for publication.

## Acceptance

Run:

```sh
make check
```

Acceptance requires:

- promotion from valid research + acquisition evidence + matching artifact succeeds;
- failed acquisition is rejected;
- artifact hash mismatch is rejected;
- acquisition claiming native activation is rejected;
- emitted proposal is `safe-test`, never `verified`;
- emitted verdict is `TEST-SIGNATURE`, never `INFECTED`;
- all previous host tests remain green.

Because the repository EICAR metadata remains `research` and the generated C table is unchanged, no FS-UAE qualification is required for M2.2g itself.

## Next gate

The next step is operator acquisition of the canonical EICAR artifact from the authoritative source and generation of the acquisition JSON plus safe-test proposal. After those pass, run clean-corpus false-positive qualification. Only then should the repository EICAR record be changed to `safe-test`, the generated native table regenerated, and visible A500/68000/Kickstart 1.2/512 KiB runtime qualification performed.
