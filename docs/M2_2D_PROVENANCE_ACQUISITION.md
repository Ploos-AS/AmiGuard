# M2.2d — Safe-test provenance and acquisition gate

## Goal

Turn the M2.2c research candidates into a reproducible acquisition workflow without activating any new native signature.

This step remains host-side only. It must not introduce `INFECTED`, must not alter the native signature table, and must not require FS-UAE runtime qualification unless a later step activates a concrete test signature.

## Current source assessment

### Zeeball AV-Testfile v1.2

Historical Amiga antivirus material documents a harmless Zeeball antivirus test file and historical xvs.library recognition for it. However, the current research pass did not establish a directly authoritative downloadable archive with sufficiently clear provenance and redistribution terms.

Therefore Zeeball remains `status=research` and blocked at the acquisition gate. Do not guess hashes, offsets, archive names, or signature bytes. Do not copy data from xvs.library.

Required before promotion:

1. authoritative or well-provenanced archive source;
2. archive SHA-256;
3. exact contained test-file path/name and SHA-256;
4. archive/file sizes;
5. license/usage/redistribution terms;
6. independent AmiGuard signature derivation from obtained bytes;
7. clean-corpus false-positive qualification;
8. visible A500/68000/Kickstart 1.2 runtime qualification if activated.

### EICAR Standard Anti-Virus Test File

EICAR publishes an authoritative specification and download page for its standard antivirus test file and explicitly describes it as a safe antivirus test artifact rather than malware. Historical Amiga antivirus release notes also document recognition of EICAR as a data-file test case.

AmiGuard therefore tracks EICAR as a second safe interoperability candidate under `signatures/files/eicar-standard-av-test-research.json`.

The record remains `status=research`: no sample SHA-256 and no production signature are present, so it is not rendered into the native table.

Authoritative reference:

- https://www.eicar.org/download-anti-malware-testfile/

## Acquisition record requirements

For any third-party safe-test artifact, record at minimum:

```text
source URL
retrieval date
publisher/maintainer
archive filename (if applicable)
archive size
archive SHA-256
contained test filename
contained file size
contained file SHA-256
license/usage terms
redistribution status
notes on whether bytes may be committed publicly
```

Hashes must be derived locally from obtained bytes. Do not copy hashes from an unrelated mirror when an authoritative source can be acquired directly.

## Lifecycle rule

Safe interoperability test artifacts are not malware samples. Their positive runtime verdict must remain distinguishable from a real malware verdict.

A future activated harmless test signature should therefore produce a test-specific result such as `TEST-SIGNATURE`, never `INFECTED`.

Real `INFECTED` remains reserved for explicitly verified, non-synthetic malware signatures under the AmiGuard lifecycle.

## Acceptance

Run:

```sh
make check
```

Acceptance requires:

- all existing C and Python tests PASS;
- bootblock and file-signature generated tables remain current;
- both Zeeball and EICAR research records remain inactive;
- generated native file-signature table is unchanged by research-only records;
- no native scanner source behavior changes.

Because M2.2d is metadata/documentation only, no new FS-UAE runtime qualification is required.

## Next step

M2.2e should acquire one safe test artifact reproducibly and record its exact local hashes and provenance. Prefer EICAR first because an authoritative current source and explicit safe-test specification are available. Keep Zeeball research open until an authoritative or sufficiently well-provenanced package is located.
