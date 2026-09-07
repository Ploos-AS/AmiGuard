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

## Community malware sample project

AmiGuard is looking for authentic historical Amiga virus and trojan samples so future detections can be backed by real evidence rather than assumptions.

**The public submission channel is live at https://amiguard.ploos.no/.**

Please use that service for suspected malware. Do **not** attach suspected malware to GitHub issues, pull requests, discussions, or repository commits.

The submission service is write-only: it accepts one sample with explicit consent, records a server-generated submission ID, SHA-256, size and receipt time, and does not expose a public retrieval endpoint. The original client filename is not retained.

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
