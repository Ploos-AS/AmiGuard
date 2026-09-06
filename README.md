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

## Build

The native target is intended for a classic m68k-amigaos cross toolchain.

```sh
make
```

Host-side qualification of the portable scanner core:

```sh
make check
```

See [docs/M0.md](docs/M0.md) for scope and acceptance criteria.

## License

MIT.
