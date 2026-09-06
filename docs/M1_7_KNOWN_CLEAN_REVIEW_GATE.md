# M1.7 — known-clean review gate

## Purpose

Add an explicit, side-effect-free preflight for promoting a `candidate-clean`
bootblock fingerprint to `verified-clean`.

The gate exists to prevent a single acquisition/import step from being enough
to label arbitrary media known-clean.

## Lifecycle

1. `tools/import_known_clean.py` emits a provenance-rich `candidate-clean`
   entry from a local image.
2. An independent review record is created separately.
3. `tools/preflight_known_clean.py` validates the candidate, review and current
   database together.
4. Only a passing preflight may produce the proposed `verified-clean` JSON.
5. Database edits remain explicit review/commit actions; the preflight tool
   never mutates the repository or input media.

## Review record schema

A review record uses schema 1 and requires:

- `candidate_id`: exact candidate ID;
- `bootblock_sha256`: exact candidate bootblock SHA-256;
- `reviewer`: independent reviewer identity/reference;
- `method`: how the candidate and provenance were independently checked;
- `evidence`: concrete evidence/reference retained by the project;
- `decision`: exactly `verified-clean`.

Example shape:

```json
{
  "schema": 1,
  "candidate_id": "example.clean",
  "bootblock_sha256": "<64 hex characters>",
  "reviewer": "independent reviewer",
  "method": "independent hash and provenance review",
  "evidence": "review record reference",
  "decision": "verified-clean"
}
```

## Preflight rules

`tools/preflight_known_clean.py` rejects promotion when any of the following is
true:

- candidate status is not `candidate-clean`;
- required candidate source/provenance metadata is absent;
- candidate bootblock or input SHA-256 is malformed;
- input size is shorter than 1024 bytes;
- review ID does not match candidate ID;
- review SHA-256 does not exactly match the candidate bootblock hash;
- reviewer, method or evidence is missing;
- decision is not exactly `verified-clean`;
- the candidate ID already exists in the database;
- the candidate bootblock SHA-256 already exists in the database.

On success, the tool emits a proposed `verified-clean` entry with structured
verification metadata. It does not write the database.

## Safety semantics

`verified-clean` means only that the exact 1024-byte bootblock fingerprint was
reviewed and accepted as known-clean under documented provenance. It is not a
general guarantee that every disk containing such a bootblock is malware-free;
files, filesystem content and memory remain separate scan domains.

This milestone does not alter the native Amiga scanner, `STANDARD`, `CUSTOM`,
`UNKNOWN` or `INFECTED` classification semantics.

## Qualification

M1.7 is host-side tooling only. Required qualification is:

- existing scanner C tests PASS;
- existing trackdisk tests PASS;
- all Python tests PASS, including M1.7 positive and negative preflight cases;
- GitHub Actions CI PASS.

No visible FS-UAE runtime requalification is required because native Amiga code
is unchanged.
