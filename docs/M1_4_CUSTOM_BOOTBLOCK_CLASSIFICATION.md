# M1.4 Custom bootblock classification

M1.4 improves bootblock reporting without requiring historical malware samples and without introducing heuristic `INFECTED` results.

## Classification model

- `INFECTED`: a compiled signature matches.
- `STANDARD`: Amiga DOS identifier (`DOS0`-`DOS7`) and valid bootblock checksum.
- `CUSTOM`: non-DOS bootblock with a valid Amiga bootblock checksum.
- `UNKNOWN`: structurally unrecognized or checksum-invalid bootblock.
- `ERROR`: malformed input or scanner error.

## Safety semantics

`CUSTOM` is deliberately neutral. A custom bootblock can be legitimate software, a game loader, a demo, a utility, or something malicious. AmiGuard must not promote `CUSTOM` to `INFECTED` without a verified malware signature or a future explicitly reviewed detection rule.

Likewise, `STANDARD` means structurally valid Amiga DOS bootblock, not malware-free.

This keeps false-positive risk low while giving users more information than the previous `UNKNOWN` result for all non-DOS bootblocks.

## Implementation

The native result enum now includes `AMIGUARD_RESULT_CUSTOM`. After signature matching, the scanner evaluates the 1024-byte bootblock checksum once. A valid non-DOS bootblock becomes `CUSTOM: custom bootblock (valid checksum)`. Invalid-checksum non-DOS bootblocks remain `UNKNOWN: unknown bootblock`.

Host regression coverage includes a valid non-DOS carry-wrap fixture and verifies that it is classified as `CUSTOM`.

## Compatibility and next gate

The code remains C89-oriented and retains the Kickstart 1.2+ / Motorola 68000 compatibility contract. Because the native scanner result and CLI output changed, M1.4 requires a short visible FS-UAE A500/Kickstart 1.2 runtime requalification before the milestone is considered runtime-complete.
