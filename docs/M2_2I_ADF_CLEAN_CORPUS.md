# M2.2i — Read-only ADF clean-file corpus extraction

## Goal

Build a reproducible local clean-file corpus from operator-selected trusted Amiga
ADF images without modifying those images and without committing third-party
Workbench/AmigaOS files to the AmiGuard repository.

This milestone is host-side tooling only. It does not activate EICAR or any other
file signature and does not change native scanner behavior.

## Source policy

The first intended source set is the user's Amiga Forever / FS-UAE Workbench and
AmigaOS floppy collection. Prefer clearly identified system media such as
Workbench/AmigaOS 1.2, 1.3.4, 2.04, 2.1, 3.0 and 3.1. Avoid cracked games,
third-party utilities, relokick disks and other uncertain material in the first
clean-corpus pass.

These ADFs are treated as `trusted-source clean candidates`, not as universally
proven clean merely because of their filename. The manifest records provenance
and hashes so later review can tighten that trust decision.

## Extractor

`tools/extract_clean_adf_corpus.py` uses `amitools`' `xdftool` to unpack ADF
contents into a local output directory.

Safety properties:

- ADF inputs are opened only for hashing by AmiGuard tooling.
- `xdftool` is invoked only with its `unpack` operation.
- each source ADF SHA-256 is computed before and after extraction;
- any source hash change aborts the run;
- symlinks are ignored in extracted output;
- extracted paths are checked to remain below their per-image output directory;
- output files and manifest remain local and are not copied into Git;
- no malware or clean verdict is inferred from an extracted file by the extractor itself.

`xdftool` is an external host dependency and is intentionally not required by CI.
Unit tests use an isolated fake extractor so CI verifies AmiGuard's wrapper,
manifest and integrity behavior without needing third-party packages.

Typical installation is via the `amitools` package appropriate for the host.
The tool also accepts `--xdftool /path/to/xdftool`.

## Manifest

The emitted schema-1 manifest has kind:

```text
amiguard-clean-file-corpus
```

For each source ADF it records:

- absolute local path;
- byte size;
- SHA-256;
- read-only integrity result;
- number of files extracted.

For each extracted regular file it records:

- source ADF index/path/hash;
- internal Amiga filesystem path as exposed by `xdftool`;
- absolute local extracted path;
- byte size;
- SHA-256.

Duplicate file hashes are grouped for later corpus analysis.

## Recommended first local run

After pulling this milestone, choose the six clearly identified Workbench images:

```sh
python3 tools/extract_clean_adf_corpus.py \
  ~/Documents/FS-UAE/Floppies/amiga-os-120-workbench.adf \
  ~/Documents/FS-UAE/Floppies/amiga-os-134-workbench.adf \
  ~/Documents/FS-UAE/Floppies/amiga-os-204-workbench.adf \
  ~/Documents/FS-UAE/Floppies/amiga-os-210-workbench.adf \
  ~/Documents/FS-UAE/Floppies/amiga-os-300-workbench.adf \
  ~/Documents/FS-UAE/Floppies/amiga-os-310-workbench.adf \
  --output-dir /tmp/amiguard-clean-corpus \
  --manifest /tmp/amiguard-clean-files.json
```

Do not place `/tmp/amiguard-clean-corpus` or its manifest under the repository.

## Connection to M2.2h

M2.2h currently accepts clean files as positional arguments. After successful ADF
extraction, the extracted paths can be supplied to `tools/preflight_safe_test.py`.
A later convenience step may teach the preflight tool to consume the corpus
manifest directly so very large corpora do not need shell-expanded argument lists.

## Acceptance

Run:

```sh
make check
```

Acceptance requires:

- all existing tests pass;
- extractor helper tests pass without a real `xdftool` dependency;
- source-hash preservation is tested;
- file hashes/internal paths are tested;
- missing `xdftool` fails cleanly;
- no native scanner or generated signature table changes occur.

No FS-UAE runtime requalification is required because this milestone is host-side
corpus tooling only.

## Next gate

Run the extractor locally against the selected Amiga Forever/FS-UAE Workbench
images. If it succeeds, inspect corpus size and provenance, then feed the corpus
into the M2.2h EICAR safe-test preflight. Native EICAR activation remains blocked
until that clean-corpus preflight passes.
