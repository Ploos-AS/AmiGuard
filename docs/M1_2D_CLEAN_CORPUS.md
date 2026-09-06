# M1.2d — Clean corpus manifest

## Goal

Make negative regression for real bootblock-virus signatures reproducible without committing disk images or malware samples to the repository.

`tools/build_clean_manifest.py` reads known-clean local media and writes a JSON manifest containing absolute input paths, input sizes, whole-input SHA-256 values, and bootblock SHA-256 values. The media itself remains local.

Example:

```sh
python3 tools/build_clean_manifest.py \
  /isolated/clean/wb12.adf \
  /isolated/clean/wb13.adf \
  /isolated/clean/custom.adf \
  -o /isolated/amiguard-clean-manifest.json
```

The manifest has schema `1` and kind `amiguard-clean-bootblock-corpus`.

## Qualification use

M1.2c candidate qualification should run the proposed offset/pattern/mask against the isolated positive sample and every clean bootblock represented by the manifest. Any clean match is a hard failure and blocks promotion to `verified`.

The manifest is evidence and inventory, not a claim that a disk is universally clean. Entries should come from trusted reference media and be identified independently where practical.

## Repository policy

- Do not commit copyrighted disk images merely to support tests.
- Do not commit live malware samples.
- Hashes and provenance notes may be committed when appropriate.
- Local paths in generated manifests can reveal workstation layout, so manifests intended for publication should be sanitized or reduced to stable labels plus hashes.

## M1.2d acceptance criteria

- read-only manifest builder supports raw bootblocks and larger disk images;
- whole-input and first-1024-byte SHA-256 values are recorded;
- inputs shorter than 1024 bytes are rejected;
- builder has host regression tests;
- tests run under `make check`;
- no native Amiga runtime dependency changes;
- no sample bytes are committed.
