# AmiGuard

AmiGuard is an open-source antivirus project for classic Amiga systems.

## M0 target

- AmigaOS / Kickstart 1.2+
- Motorola 68000
- CLI-first
- 512 KiB-friendly design
- Bootblock scanning first
- No OS 2.x-only APIs in the runtime path

M0 establishes the portable scanner core, a compact signature format, a
Kickstart 1.2-compatible Amiga CLI shell, host-side qualification tests, and
the first bootblock classification logic.

## Help AmiGuard find and preserve Amiga malware

AmiGuard needs authentic historical Amiga virus and trojan samples. Real samples let us independently analyse malware, reproduce detections, build signatures, test them against clean software, and eventually replace temporary external detection sources with AmiGuard's own verified signatures.

**Submit suspected malware at https://amiguard.ploos.no/.**

Please submit the original suspicious material whenever possible. Useful submissions include:

- suspicious Amiga executable files and programs;
- files reported as infected by another antivirus, including `xvs.library`-based scanners;
- infected or suspicious disk images such as ADF files;
- bootblock samples or complete disk images when a bootblock virus is suspected;
- archived historical malware collections when you have the right to provide them;
- files from old Amiga disks that behave suspiciously even when the malware family is unknown.

For an infected floppy, a **complete disk image is preferred** when practical. It preserves the bootblock and other context that may be important for analysis. If only one infected executable is available, submit that original file instead. Do not intentionally modify, disinfect, repack, or rename a sample before submission unless necessary to transport it: the exact bytes are valuable evidence.

If an antivirus identifies the sample, include the reported virus/trojan name and scanner name/version in the submission notes. In particular, an AmiGuard `XVS-DETECTED` result means that optional `xvs.library` support has reported something that AmiGuard has **not yet independently verified**. Those samples are especially useful: please submit the suspicious file or disk image and mention the `XVS-DETECTED` name in the notes.

### Why your sample matters

AmiGuard deliberately does not label malware `INFECTED` merely because another scanner names it. A real sample allows the research pipeline to hash and preserve the original, perform static and isolated runtime analysis, derive an independent candidate signature, test it against a clean corpus, and qualify the resulting AmiGuard detection. Community submissions therefore directly help turn historical detections into independently verified open AmiGuard signatures.

The goal is not to collect as many files as possible. The most valuable submissions are authentic, unmodified samples with useful provenance: where the file/disk came from, what unusual behaviour was observed, and what existing antivirus detected it, if known.

### Safe submission

Treat suspected samples as malware. Do not run them on a normal Amiga, emulator with important writable disks, or everyday computer merely to test them. Upload the existing sample directly through the submission service.

Do **not** attach suspected malware to GitHub issues, pull requests, discussions, or repository commits. Do not submit software you do not have the right to provide, unrelated personal files, or deliberately fabricated malware.

The public submission service is write-only: it accepts one sample with explicit consent, records a server-generated submission ID, SHA-256, size and receipt time, and does not expose a public retrieval endpoint. The original client filename is not retained.

See the [sample submission page](docs/SAMPLE_SUBMISSION.md) and the [GitHub Pages landing page](docs/index.html) for submission guidance, privacy/retention notes, and the research workflow.

## Build

The native target is intended for a classic m68k-amigaos cross toolchain.
The default build uses `m68k-amigaos-gcc`, `-m68000` and the toolchain's
`-mcrt=nix13` runtime to avoid OS 2.x dependencies.

```sh
make
```

Host-side qualification of the portable scanner core:

```sh
make check
```

See [docs/M0.md](docs/M0.md) for scope and acceptance criteria.
See [M0.3 runtime qualification](docs/M0_3_RUNTIME_QUALIFICATION.md) for the
observed Kickstart/Workbench 1.2 results and the reproducible visible FS-UAE test.

## License

MIT.
