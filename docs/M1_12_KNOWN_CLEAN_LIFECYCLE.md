# M1.12 Known-clean lifecycle hardening

M1.12 closes the direct promotion bypass in the known-clean import path.

## Lifecycle

The supported lifecycle is now:

1. `tools/import_known_clean.py` reads local media/images and emits only a `candidate-clean` entry.
2. The importer is read-only with respect to input media and does not mutate `known-clean/bootblocks.json`.
3. The importer does not expose `--status` or `--verifier` and cannot emit `verified-clean`.
4. Independent review evidence is supplied to the M1.7 `tools/preflight_known_clean.py` gate.
5. Only a successful M1.7 preflight may propose `candidate-clean -> verified-clean` metadata.

This makes independent review a mandatory lifecycle boundary rather than an optional convention.

## Semantics

`candidate-clean` is not treated as a trusted known-clean fingerprint by the identifier. It may be matched and displayed as `CANDIDATE-CLEAN`, but `known_clean` remains false until the entry is promoted through the review gate.

`verified-clean` remains the trusted non-test lifecycle state and requires verification metadata validated by the existing known-clean database/preflight tooling.

## Regression coverage

M1.12 tests verify that:

- normal import emits `candidate-clean`;
- emitted candidate verification is null;
- `--status verified-clean` is rejected because the option no longer exists;
- `--verifier` is rejected because the option no longer exists;
- the internal entry builder always emits `candidate-clean`;
- short inputs remain rejected.

## Runtime qualification

No native Amiga source, generated signature table, trackdisk code, or executable behavior changes in M1.12. Host tests and CI are therefore the qualification gate; FS-UAE runtime requalification is not required.
