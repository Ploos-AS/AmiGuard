# AmiGuard v0.1.0 release candidate

The next public target is AmiGuard v0.1.0.

## Purpose

The first public release is intended to put the native scanner into real Amiga users' hands and make it easy for the community to contribute authentic suspicious Amiga files and disk images through https://amiguard.ploos.no/.

The release must clearly separate AmiGuard's own verdicts from the optional transitional xvs.library bridge:

- `INFECTED` means an independently qualified AmiGuard production signature matched.
- `XVS-DETECTED` means the optional xvs.library bridge reported a detection that AmiGuard has not independently verified yet.
- `TEST-SIGNATURE` is reserved for harmless qualification fixtures.

## Candidate contents

The release package must contain:

- `AmiGuard` native 68000 executable;
- `README.md`;
- `LICENSE`;
- `RELEASE.txt`;
- `SHA256SUMS`;
- `docs/SAMPLE_SUBMISSION.md`;
- `docs/M2_3_XVS_BRIDGE.md`.

`xvs.library` is not bundled. Users who already have a compatible xvs.library may use the bridge automatically; AmiGuard must remain usable without it.

## Qualification gates before v0.1.0 tag

1. Host regression suite passes on the exact release commit.
2. FS-UAE/AROS provisional qualification passes on the exact release commit.
3. Native package is produced with `tools/package_release.sh` and checksums recorded.
4. Visible A500 / 68000 / Kickstart 1.2 qualification passes with the release-candidate binary.
5. Verify operation with xvs.library absent: AmiGuard still scans normally.
6. Verify an xvs-enabled runtime path without allowing xvs results to become `INFECTED` verdicts.
7. Verify README and release notes direct users to https://amiguard.ploos.no/ and explain which files/disk images are useful to submit.
8. Only after the above gates pass, create the `v0.1.0` tag and GitHub Release.

## Community message

AmiGuard needs original, unmodified suspicious Amiga files and, where practical, complete disk images. Full disk images are especially valuable for bootblock cases because they preserve context that an isolated file may not contain. If another scanner names a detection, contributors should include the scanner and reported name in the submission notes.

The aim is to turn community submissions into independently analysed, clean-corpus-tested, native-qualified AmiGuard signatures so the transitional external bridge can become less important over time.
