# M1.2 — Research-to-verified gate

## Goal

Introduce the first real historical bootblock-virus research records without allowing unverified material into AmiGuard's native detection table.

M1.2 separates three states:

- `test-only`: synthetic regression fixtures; compiled into the native table.
- `research`: documented candidate families/markers; never compiled into the native table.
- `verified`: non-synthetic detections backed by a recorded sample SHA-256, stable signature evidence, clean-media regression checks, and isolated sample validation; compiled into the native table.

No live malware is committed to this repository.

## First research candidate

The first candidate is the historical Mount / Eleni 2.2 bootblock virus documented by Virus Help Team. The public description identifies it as a 1024-byte bootblock/file virus and documents an invariant encoded text marker near the top of the bootblock. The research record preserves only the candidate metadata needed to guide isolated verification; it is not a claimed detection signature yet.

Before promotion to `verified`, AmiGuard requires:

1. a legally analyzable isolated sample;
2. SHA-256 of the analyzed bootblock/sample;
3. independently measured exact offset and bytes from that sample;
4. confirmation that the candidate marker is stable across available variants;
5. negative regression against clean Workbench and known custom bootblocks;
6. runtime detection validation on the Kickstart 1.2 scanner;
7. provenance notes documenting how the signature was derived.

## Safety rule

A public encyclopedia description is research evidence, not sufficient proof for a production signature. Research entries must therefore be excluded from `src/signatures_generated.inc` until promoted to `verified`.

## M1.2a acceptance criteria

- metadata compiler accepts incomplete non-synthetic `research` entries with no sample hash/signature;
- research entries are validated but excluded from native generated output;
- non-synthetic `verified` entries still require a 64-hex SHA-256 and concrete signature;
- `test-only` synthetic fixtures continue to compile and pass existing tests;
- generated table remains deterministic;
- no new runtime dependency is introduced;
- no malware bytes or sample are committed.

## M1.2b — Local sample analyzer

`tools/analyze_bootblock.py` provides a reproducible, read-only host-side analysis step for isolated samples. It accepts either a raw 1024-byte bootblock or a larger disk image such as an ADF and analyzes only the first 1024 bytes as the bootblock.

Example:

```sh
python3 tools/analyze_bootblock.py /isolated/sample.adf
```

Machine-readable output:

```sh
python3 tools/analyze_bootblock.py /isolated/sample.adf --json
```

The report contains:

- total input size;
- SHA-256 of the complete input;
- SHA-256 of the 1024-byte bootblock;
- DOS type when the bootblock begins with a supported `DOS` identifier;
- Amiga bootblock checksum status;
- printable ASCII strings and their exact byte offsets.

A research metadata draft can be produced with:

```sh
python3 tools/analyze_bootblock.py /isolated/sample.adf \
  --draft \
  --id mount-eleni.sample1 \
  --name "Mount / Eleni sample 1" \
  --family "Mount / Eleni" \
  --source "isolated local sample"
```

The draft is deliberately `status: research`, has `signature: null`, and sets the verifier to `pending`. The analyzer never promotes a sample to `verified` and never chooses signature bytes automatically.

This boundary is intentional: candidate signature offsets, byte patterns and masks must be selected only after comparing isolated positive samples against clean media and, where possible, multiple variants of the same family. This prevents one arbitrary byte sequence from being mistaken for a stable family signature.

The analyzer opens inputs read-only. Tests verify that analysis leaves the input SHA-256 unchanged and that short inputs are rejected.

## M1.2b acceptance criteria

- raw 1024-byte bootblocks and larger disk images are supported;
- complete-input and bootblock SHA-256 values are reported independently;
- DOS type and checksum state are reported;
- printable strings include exact offsets;
- input files are never modified;
- research-draft output cannot claim `verified` status or generate a concrete signature;
- analyzer tests run as part of `make check`;
- no malware sample or malware-derived payload is committed.

## Handoff to M1.2c

M1.2c is the first real signature qualification. Use the analyzer on an isolated local/RAB sample set, compare candidate evidence across samples and clean media, then promote only a detection that passes:

1. recorded sample/bootblock SHA-256;
2. independently derived stable offset/pattern/mask;
3. positive isolated-sample detection;
4. negative clean-media/custom-bootblock regression;
5. visible Kickstart 1.2 runtime detection;
6. documented provenance.
