# M1.2c — Signature qualification gate

## Goal

Make promotion from `research` to `verified` reproducible and conservative.

AmiGuard now has a host-side qualification tool:

```sh
python3 tools/qualify_signature.py \
  /isolated/sample.adf \
  --clean-manifest /isolated/clean-manifest.json \
  --offset 123 \
  --pattern a1b2c3d4 \
  --mask ffffffff
```

The tool is read-only. It never edits the sample, clean media, or repository metadata.

## Clean manifest

The clean corpus remains outside the repository. A manifest points at local files:

```json
{
  "schema": 1,
  "entries": [
    {
      "path": "/isolated/clean/workbench-1.2.adf",
      "bootblock_sha256": "optional-known-bootblock-sha256"
    },
    {
      "path": "/isolated/clean/custom-known-good.adf"
    }
  ]
}
```

When `bootblock_sha256` is present, qualification also verifies that the local clean fixture is the expected one.

## Gate

A candidate qualifies only when all of the following are true:

1. the proposed offset/pattern/mask matches the isolated positive sample;
2. no clean-manifest bootblock matches the proposed signature;
3. all supplied clean fixture hashes match;
4. the sample and all clean inputs are at least 1024 bytes;
5. pattern and mask are valid hex and equal length.

A successful host qualification is necessary but not sufficient for final `verified` status. Human review of provenance and signature stability across known variants remains required, followed by native Kickstart 1.2 runtime validation.

## Safety and repository policy

- no malware sample is committed;
- no clean disk image needs to be committed;
- local absolute paths stay in local qualification output and are not intended for checked-in metadata;
- a failed clean regression blocks promotion;
- the tool does not generate or write a `verified` metadata record automatically.

## M1.2c acceptance criteria

- exact and masked candidate matching are supported;
- positive sample mismatch fails qualification;
- any clean false positive fails qualification;
- optional clean bootblock hash mismatch fails qualification;
- qualification tests are included in `make check`;
- no new AmigaOS runtime dependency is introduced.

## Next

M1.2d uses this gate with a real isolated historical sample. Once a candidate passes positive/negative qualification and provenance review, its metadata can be promoted manually to `verified`, compiled into the native table, and runtime-tested on the Kickstart 1.2 / 512 KiB profile.
