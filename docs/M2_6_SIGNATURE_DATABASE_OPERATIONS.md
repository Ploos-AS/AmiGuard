# M2.6 — Production signature database operations

M2.6 makes the AmiGuard signature set reproducible and auditable without weakening the existing promotion gates.

## Database manifest

`tools/build_signature_manifest.py` inventories signature metadata below `signatures/` and generates `signatures/manifest.json`.

The manifest contains:

- manifest schema version;
- signature database version;
- deterministic database identity;
- total metadata record count;
- inventory grouped by signature kind/status;
- exact production-signature inventory.

A production signature is defined narrowly as a non-synthetic record with `status: verified`. Qualified, research, safe-test and test-only records do not enter the production identity.

## Deterministic identity

The database identity is SHA-256 over canonical JSON describing only the sorted production-signature inventory. This means changes to research or test records do not masquerade as a production database change, while adding/removing/changing an activated verified signature changes the identity deterministically.

## Version policy

`database_version` starts at 1. It is an explicit format/operations generation, not a count of malware signatures and not an application release number. Change it only when the database contract itself changes incompatibly or a documented operational migration requires a new generation.

## Update policy

1. Research/sample intake never changes the active production set.
2. A candidate must pass the existing review, clean-corpus, qualification and native finalization gates.
3. Only a reviewed `verified`, non-synthetic record may be activated in the signature metadata tree.
4. Regenerate native signature tables as applicable.
5. Regenerate `signatures/manifest.json`.
6. Run the full host regression suite and required native qualification.
7. Release packaging must carry a manifest consistent with the source tree.

No network updater is introduced by M2.6. Signature transport/update mechanisms are a separate future concern and must preserve authenticity, rollback and compatibility guarantees.

## Commands

Regenerate:

```sh
python3 tools/build_signature_manifest.py --write
```

Verify:

```sh
python3 tools/build_signature_manifest.py --check
```

M2.6 is complete when the manifest generator, deterministic identity tests, checked-in manifest and CI consistency gate are all green.
