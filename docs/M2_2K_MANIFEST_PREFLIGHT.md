# M2.2k — Manifest-based safe-test preflight

M2.2k removes the need to pass hundreds of extracted clean files as individual
command-line arguments to `tools/preflight_safe_test.py`.

The preflight tool now accepts one or more `--clean-manifest` arguments. Each
manifest must use schema 1 and kind `amiguard-clean-file-corpus`, as emitted by
`tools/extract_clean_adf_corpus.py`.

Before any signature comparison, every manifest entry is re-read and checked
against its recorded size and SHA-256. A stale, changed, malformed or missing
corpus file therefore fails closed. Explicit clean-file arguments remain
supported and may be combined with manifests; duplicate real paths are tested
only once.

Example:

```sh
python3 tools/preflight_safe_test.py \
  signatures/files/eicar-standard-av-test.json \
  /home/pgo/Downloads/eicar.com.txt \
  --clean-manifest /tmp/amiguard-clean-files.json \
  -o /tmp/eicar-preflight.json
```

The tool remains read-only and host-side. It does not activate signatures,
change native verdict semantics, or make a malware-detection claim. EICAR
remains a harmless antivirus interoperability safe-test.

## Qualification gate

M2.2k is complete when:

- host tests cover manifest success and integrity failures;
- `make check` passes on the exact final commit;
- a real `amiguard-clean-file-corpus` manifest can be consumed without passing
  its files as positional arguments;
- the resulting safe-test preflight still reports the same clean corpus count
  and no signature collisions.

No FS-UAE runtime qualification is required because M2.2k changes host-side
preflight tooling only and does not alter native AmiGuard code or generated
native signature tables.
