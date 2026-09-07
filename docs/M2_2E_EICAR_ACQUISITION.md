# M2.2e — Reproducible EICAR acquisition qualification

## Goal

Provide a reproducible host-side gate for an independently obtained canonical
EICAR Standard Anti-Virus Test File without activating a new native AmiGuard
signature.

This milestone does not commit the EICAR test file itself, does not change the
native signature table, and does not introduce `INFECTED` or a new
`TEST-SIGNATURE` result.

## Authoritative specification

EICAR currently publishes the test-file specification and download area at:

- https://www.eicar.org/download-anti-malware-testfile/

The publisher states that the canonical `eicar.com` and `eicar.com.txt` forms are
68 bytes and describes the test file as safe/non-viral test material. EICAR also
encourages use of the test file for antivirus testing.

For the exact canonical 68-byte form, independently hashing the bytes specified
by EICAR yields:

```text
size:   68
sha256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
```

This value is a specification-derived acquisition check. It is not placed in the
`sample_sha256` field of the existing `status=research` signature record, because
that lifecycle field remains reserved for a separately qualified concrete
signature/sample transition.

## Qualification tool

`tools/qualify_eicar_acquisition.py` accepts a locally obtained file and records:

- source URL;
- retrieval date/timestamp;
- local filename;
- local byte size;
- locally computed SHA-256;
- comparison with the canonical 68-byte specification;
- explicit `malware_claim=false`;
- explicit `native_activation=false`.

Example:

```sh
python3 tools/qualify_eicar_acquisition.py \
  /path/to/eicar.com.txt \
  --source-url https://www.eicar.org/download/eicar.com.txt \
  --retrieved-at 2026-09-07 \
  --json > /tmp/amiguard-eicar-acquisition.json
```

The operator must use the actual authoritative download URL observed during the
retrieval. Do not substitute a mirror merely to obtain a matching hash.

Exit status:

- `0`: exact canonical 68-byte EICAR file;
- `1`: file read successfully but size/hash does not match canonical form;
- `2`: acquisition file could not be read.

## Redistribution policy

The EICAR page explicitly makes the test file available for antivirus testing
and describes it as safe to pass around. AmiGuard nevertheless does not infer a
software-license grant for embedding third-party bytes in this repository from
that statement alone.

M2.2e therefore records acquisition/provenance only. The EICAR bytes are not
committed to the public repository in this step.

## Tests

`tests/test_qualify_eicar_acquisition.py` verifies:

- canonical 68-byte input passes;
- one-byte near-miss fails;
- JSON CLI reporting remains stable;
- the report never claims malware or native activation.

Run:

```sh
make check
```

## Acceptance

M2.2e tooling is ready when:

1. CI passes on the exact repository HEAD;
2. the existing EICAR metadata remains `status=research`;
3. `sample_sha256` and `signature` remain null in that research record;
4. the native generated signature table is unchanged;
5. the acquisition qualifier can validate an independently obtained canonical
   68-byte file and emit a provenance report;
6. no FS-UAE qualification is required because native behavior is unchanged.

The acquisition itself is complete only after an operator obtains the file from
the authoritative EICAR source and records the resulting local provenance JSON.
That local evidence may be summarized in this document without committing the
third-party file bytes.

## Next gate

After authoritative acquisition passes, derive an AmiGuard-specific harmless
interoperability signature independently from the acquired bytes and qualify it
against the clean corpus. If that signature is activated natively, it must report
`TEST-SIGNATURE`, never `INFECTED`, and must undergo visible
A500/68000/Kickstart 1.2/512 KiB runtime qualification.
