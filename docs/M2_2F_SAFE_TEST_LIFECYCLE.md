# M2.2f — External harmless safe-test lifecycle

## Goal

Add an explicit lifecycle state for externally produced harmless antivirus test artifacts such as EICAR, without conflating them with either synthetic AmiGuard fixtures or verified malware.

## New status: `safe-test`

`safe-test` is reserved for a non-synthetic harmless interoperability/test artifact whose exact bytes and provenance have been independently qualified.

A `safe-test` record must:

- be `synthetic=false`;
- carry an exact 64-hex SHA-256 in `sample_sha256`;
- carry a concrete fixed-offset masked signature within the 128 KiB intake bound;
- carry non-empty source, provenance, and verifier metadata;
- use `cleaner=none`;
- never be treated as a malware signature.

The compiler renders `safe-test` entries into the native file-signature table with the same native `test_only=1` verdict flag used by AmiGuard's synthetic `test-only` fixture. Consequently a native match can only reach `TEST-SIGNATURE`, never `INFECTED`.

## Lifecycle separation

The file-signature statuses now have distinct roles:

- `test-only`: synthetic AmiGuard-only qualification fixture; no sample hash; active only as `TEST-SIGNATURE`.
- `research`: non-synthetic candidate/reference; no sample hash and no concrete signature; inactive.
- `safe-test`: externally produced harmless test artifact; exact hash + concrete signature; active only as `TEST-SIGNATURE`.
- `qualified`: sample-backed malware candidate after host qualification; inactive.
- `verified`: explicitly verified non-synthetic malware signature; active as real malware detection and eligible for `INFECTED`.

This prevents the EICAR path from being forced through the malware `qualified -> verified` lifecycle merely to become a native harmless interoperability test.

## EICAR

The existing EICAR metadata remains `status=research` in M2.2f. This milestone does not activate EICAR yet.

Promotion to `safe-test` requires, at minimum:

1. authoritative acquisition/provenance PASS under M2.2e;
2. exact canonical file hash recorded from the acquired bytes;
3. an independently derived AmiGuard signature;
4. clean-corpus false-positive qualification;
5. explicit review that the artifact is harmless test material;
6. visible A500/68000/Kickstart 1.2/512 KiB runtime qualification after activation.

No EICAR bytes need to be committed to the repository.

## Native safety property

The generated C row carries an integer verdict flag. The compiler sets it to:

- `1` for `test-only` and `safe-test`;
- `0` only for `verified`.

The existing native intake path maps flag `1` to `AMIGUARD_FILE_TEST_SIGNATURE` / `TEST-SIGNATURE` and flag `0` to `AMIGUARD_FILE_INFECTED` / `INFECTED`.

Therefore adding a future `safe-test` entry cannot produce `INFECTED` unless that safety mapping is changed separately.

## Qualification

Run:

```sh
make check
```

Acceptance requires:

- repository generated table remains current;
- existing research records remain inactive;
- `qualified` remains inactive;
- `verified` renders with native verdict flag `0`;
- `safe-test` renders with native verdict flag `1`;
- `safe-test` rejects missing hashes, synthetic records, and cleaners;
- all existing host tests pass.

Because no repository record is promoted to `safe-test` in this milestone and the generated native table remains byte-for-byte unchanged, no new FS-UAE runtime qualification is required for M2.2f itself.

## Next gate

M2.2g should perform the first concrete safe-test promotion, preferably EICAR after authoritative acquisition evidence is available. That step must derive the concrete signature from the independently qualified bytes, run false-positive checks, regenerate the native table, and then require visible Kickstart 1.2 runtime qualification proving `TEST-SIGNATURE` and never `INFECTED`.
