# M2.2c — Safe test corpus research gate

## Goal

Establish a conservative research path for externally produced harmless antivirus
test material before AmiGuard treats any such material as a positive test vector.

This milestone does **not** add a real malware signature, does not change native
scanner behavior, and does not grant redistribution rights to third-party files.

## Zeeball AV-Testfile v1.2

Zeeball AV-Testfile is the first research target because historical Amiga
antivirus references describe it as a harmless antivirus test file and historical
xvs.library release notes document special recognition for it.

AmiGuard records it only as `status=research` until all of the following are
independently established:

1. the archive is obtained from an authoritative or well-provenanced source;
2. archive and contained test-file SHA-256 values are recorded;
3. archive contents and exact file intended for testing are documented;
4. license, redistribution, and usage terms are recorded;
5. AmiGuard derives any test signature independently from the obtained bytes;
6. false-positive checks are run against a clean corpus;
7. native visible A500/68000/Kickstart 1.2 qualification proves the expected
   harmless positive-test result;
8. the result is represented as a test/interoperability verdict, not as evidence
   that the file contains real malware.

Until those gates pass, no Zeeball archive or test-file bytes are committed to
this repository and no native signature is generated from the record.

## VirusZ_III.Bootblocks

`VirusZ_III.Bootblocks` is tracked separately as a potential bootblock
reference/known-clean research source. Public descriptions indicate that the
file is intended for VirusZ III bootblock identification and that VHT has
maintained the collection over time.

AmiGuard must not copy or transform that database into its public known-clean
corpus until format, provenance, license, and redistribution terms are clear.
If permitted, import must preserve source provenance and remain distinct from
malware-signature activation.

## xvs.library

xvs.library may serve as a comparison oracle during isolated research, but it is
not an AmiGuard runtime dependency and its recognition/disinfection data must
not be copied into AmiGuard without explicit licensing and provenance support.

## Repository state in M2.2c

The repository adds only a Zeeball research metadata record under
`signatures/files/`. By the file-signature lifecycle contract:

- `research` has no sample SHA-256;
- `research` has no production signature;
- `research` is not rendered into the native file-signature table;
- no `INFECTED` or `TEST-SIGNATURE` result is introduced by this milestone.

Run:

```sh
make check
```

Acceptance requires the existing file-signature compiler to accept the research
record while proving that generated native tables remain unchanged by the
research-only entry.

Because there is no native behavior change, no new FS-UAE runtime qualification
is required for M2.2c itself. Runtime qualification becomes mandatory if a
future step activates an independently derived harmless test signature.

## Next gate

The next operational step is acquisition/provenance qualification, not native
activation. Record the exact source, hashes, contents, and license/redistribution
terms for Zeeball AV-Testfile v1.2 before creating a concrete signature record.
