# Runtime signature database foundation

This document defines the first runtime-loadable signature database used by the AmiGuard family.

## Goal

AmiGuard historically compiled file signatures into `file_signatures_generated.inc`. That remains the built-in fallback, but it cannot be updated without rebuilding the executable.

The runtime database adds a small Amiga-friendly layer that can replace the active file-signature table after startup without changing scanner semantics or requiring networking/TLS code in the scanner.

## Format v1

The database is UTF-8/ASCII text and starts with:

```text
AMIGUARD-FILE-SIGDB 1
```

Blank lines and lines beginning with `#` are ignored. Each signature record is:

```text
FILE|name|offset|test_only|pattern_hex|mask_hex
```

Example:

```text
AMIGUARD-FILE-SIGDB 1
FILE|Example.Marker|4|1|414d494755415244|ffffffffffffffff
```

Fields:

- `name`: stable human-readable detection name, maximum 79 characters in v1;
- `offset`: decimal byte offset in the scanned file;
- `test_only`: `0` or `1`;
- `pattern_hex`: non-empty even-length hexadecimal pattern, maximum 64 bytes;
- `mask_hex`: hexadecimal mask of exactly the same length.

The current runtime limit is 64 file signatures. These limits are intentional for a small deterministic 68000 implementation and can be versioned later.

## Safety and activation semantics

`amiguard_file_signature_load_database()` parses the entire candidate into staging storage first. A malformed header, unsupported record kind, invalid offset/flag, malformed hex, pattern/mask length mismatch, oversized record, read failure, empty database, or capacity overflow rejects the candidate.

A failed load leaves the previously active signature table unchanged. A successful load atomically switches the scanner-facing table to the validated runtime database.

`amiguard_file_signature_use_builtin()` restores the generated built-in table.

The scanner obtains signatures only through `amiguard_file_signatures()`, so compiled-in and runtime signatures use the same matching path.

## Update architecture

This milestone deliberately does not fetch from the network and does not claim package authenticity. It establishes the runtime primitive required by AmiGuard AE `SIGNATURE.UPDATE`.

A later update layer should:

1. obtain a candidate package using a separate transport layer;
2. validate manifest/schema/version and integrity/authenticity;
3. stage the database to a temporary path;
4. call the runtime loader as the final semantic validation gate;
5. replace the installed database atomically with rollback support;
6. expose active source/version/status through AmiGuard AE.

Keeping transport/package verification outside the matcher avoids adding HTTP/TLS dependencies to the classic 68000 scanner core.

## Qualification

Host qualification covers:

- built-in table remains the default;
- valid runtime database activates and matches;
- runtime metadata is preserved;
- invalid replacement is rejected without disturbing the active runtime table;
- built-in fallback can be restored.

Classic Amiga runtime qualification can be added after the database path/install convention is defined by the AE update layer.
