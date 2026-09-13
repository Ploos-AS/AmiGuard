# M2.3 — Optional transitional xvs.library bridge

M2.3 adds optional transitional support for `xvs.library` while AmiGuard's independent signature database is still being built.

## Contract

- AmiGuard remains standalone and keeps its AmigaOS/Kickstart 1.2+ target.
- `xvs.library` is detected at runtime and is never required for startup or normal scanning.
- If the library is absent, too old, fails self-test, or cannot allocate its scan object, AmiGuard continues with its own engine.
- xvs results are reported as `XVS-DETECTED`, never as AmiGuard `INFECTED`.
- AmiGuard does not vendor or redistribute the xvs signature database.
- The bridge is read-only: no repair or delete operations are requested.
- A positive xvs result asks the user to submit the original suspicious file or disk image to `https://amiguard.ploos.no/` for independent analysis.
- The long-term goal is to replace useful xvs-only detections with independently qualified AmiGuard signatures.

## Verdict separation

`INFECTED`: matched by an independently verified AmiGuard production signature.

`XVS-DETECTED`: optional xvs.library reported a detection that AmiGuard has not yet independently verified.

`TEST-SIGNATURE`: harmless test-only detection used to qualify the scanner path.

## Scope

The native bridge covers both file buffers and 1024-byte bootblocks. AmiGuard's own signature engine always runs first. xvs is consulted only as a secondary source when AmiGuard has not already produced its own verified detection.

Host-side tests remain independent of xvs. Native builds enable the bridge with `AMIGUARD_NATIVE_XVS=1` and open `xvs.library` version 33 at runtime.

M2.3 does not change the final release gate: native behavior changes still require visible A500/68000/Kickstart 1.2 qualification before release certification.
