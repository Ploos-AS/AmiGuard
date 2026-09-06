# M2.1 — Read-only file intake

## Goal

Expose the M2.0 HUNK parser through a safe, read-only single-file CLI path on
Kickstart 1.2+ / Motorola 68000.

M2.1 is format intake only. It does **not** claim malware detection and does
not clean, modify, rename, quarantine, or otherwise write to the target file.

## CLI contract

Preserve the existing floppy bootblock CLI unchanged:

```
AmiGuard DF0:
```

Add an explicit file mode so AmigaDOS paths cannot be confused with floppy
unit names:

```
AmiGuard FILE <path>
```

The file is opened read-only, read into bounded memory, passed to
`amiguard_parse_hunk()`, then closed and released on every path.

Neutral output classes:

- `VALID-HUNK` — structurally valid HUNK executable/object according to the
  parser supported by AmiGuard.
- `NOT-HUNK` — input does not begin with an Amiga HUNK header.
- `MALFORMED-HUNK` — input begins as HUNK but fails structural validation.
- `ERROR` — file/open/read/allocation/size failure; not a malware verdict.

None of these classes means infected, suspicious, or clean.

## Safety and compatibility requirements

- C89-compatible implementation.
- Motorola 68000 and `-mcrt=nix13` remain mandatory.
- No OS 2.x-only APIs.
- File access is read-only.
- Reject files that cannot be represented safely by the implementation before
  allocation/read; no integer wrap or partial-buffer parsing.
- Allocation/read failures must clean up deterministically.
- Existing DF0:–DF3: behavior and bootblock result semantics remain unchanged.
- No signature matching, heuristic malware verdict, cleaner, quarantine, or
  file write path is introduced in M2.1.

## Tests

Host tests must cover the file-intake policy/helpers where practical and keep
all M2.0 HUNK parser tests. At minimum verify valid HUNK, non-HUNK, malformed
HUNK, empty/short input, bounded-size rejection, and unchanged bootblock
behavior.

Native qualification must use one visible FS-UAE instance with the established
A500 / 68000 / Kickstart 1.2 / Workbench 1.2 / 512 KiB profile. Exercise all
three neutral file classifications using harmless fixtures, verify repeated
runs are stable, and hash every fixture before/after to prove read-only
behavior.

## Completion gate

M2.1 is complete only when host tests, native build, visible KS1.2/512 KiB
runtime qualification, media/file integrity checks, and final CI on the exact
qualified HEAD all PASS.
