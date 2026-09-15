# M3.3 — ADF/full-disk image scan

Status: **DONE / PASS**

M3.3 extends AmiGuard's read-only disk engine to bounded full-disk image scanning while preserving the existing detector trust boundaries.

## Implemented

- Bounded, sector-aligned ADF traversal through `amiguard_scan_adf_readonly()`.
- Standard DD ADF size support (`901120` bytes) with a 4096-byte streaming buffer.
- The first 1024 bytes are inspected through the established AmiGuard bootblock scanner rather than a separate image-only detector.
- Remaining image data is accounted for as bounded read-only raw regions.
- The image interface exposes `read_at` only; there is no write, repair or disinfection operation.
- Malformed size, read failures, object limits and raw-byte limits fail explicitly instead of being reported as clean.
- Synthetic clean/safe-test qualification paths remain separated from production malware verdicts.
- The disk/image layer does not promote test evidence into production `INFECTED` status.

Filesystem-visible file scanning remains delegated to the established file/disk provider boundary rather than creating a second file detector inside the image scanner. This keeps file, bootblock and disk verdict authority consistent.

## Qualification

Head used for final M3.3 qualification: `34bfea6bc8240affc3eccd5cbec7cedd97350ae7`.

GitHub Actions results:

- FS-UAE AROS provisional qualification run **#65**, run ID **34974350915**: **PASS**.
- Release packages run **#48**, run ID **34974351078**: **PASS**.
- Host regression gates inside the qualification workflow: **PASS**.
- Native Bebbo/m68k build and AROS guest detector gates: **PASS** as part of the successful qualification workflow.

The AROS/FS-UAE workflow is provisional automation evidence. M3.4 remains responsible for the consolidated disk runtime qualification, including visible classic-Amiga runtime evidence, low-memory operation and malformed-media behavior across volume, raw floppy and image paths.

## Safety/trust boundary

M3.3 adds no malware sample bytes and does not relax signature activation rules. Production `INFECTED` verdicts still require independently verified production signatures. M2.5 therefore remains open until an authentic, lawfully obtained sample completes the production-signature pipeline.
