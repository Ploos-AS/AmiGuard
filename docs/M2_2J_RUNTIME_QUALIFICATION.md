# M2.2j — EICAR native runtime qualification

**Runtime qualification PASS — 2026-09-07.** All required gates were run
in one visible FS-UAE session, with GUI screenshots inspected. No headless
runtime was used. No AmiGuard code or antivirus semantics were changed.

**EICAR is a harmless safe-test, not malware. The native verdict is
TEST-SIGNATURE, never INFECTED. This is not a malware-detection claim.**
No real malware was generated, acquired or used.

## Exact input state

The repository was clean on main, with tested HEAD
`c420b945806d922c5dd8e667669d7b73f66e92e2`.
The existing native binary was used without rebuilding:
SHA-256 `72f123101cc54d5b96ee5f7b665c2848ce53a0fdd7c5d8bf2b01621be2b67fde`.
The staged binary and the repository binary still matched after testing.

Canonical input: `/home/pgo/Downloads/eicar.com.txt`, exactly 68 bytes,
SHA-256 `275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f`.
Near-miss construction copied those bytes and XORed only the last byte with 1;
the original was never changed. `eicar-nearmiss.bin` is 68 bytes, SHA-256
`7acec19c03e8fd454bc0a5d56077896d0c29db365dcd586f89a3002173be2139`.

## Runtime and resolved environment blocker

- FS-UAE **3.2.35**, visible window, 960 × 720, neither hidden nor minimized.
- A500, Motorola **68000**, cycle-exact, no JIT.
- Kickstart **1.2 / 33.180**, Workbench **1.2 / 33.56**, shown by Version
  in [startup.png](evidence/m2.2j/startup.png).
- **512 KiB Chip RAM**, zero Slow/Fast/motherboard RAM. The runtime probe
  reports zero free Fast RAM; its Exec library version is 33.192 and DOS
  library version is 33.124, distinct from the displayed Kickstart version.
- Reference: `/home/pgo/Projects/Amiga/FS-UAE_Config/fs-uae-amiga-reference-configs/a500/stock/a500-stock-accurate.fs-uae`.
  Reference, ROM and original Workbench hashes match the earlier M2.2b run.

The qualified M2.2b machine settings were reused unchanged. Only disposable
storage/output paths changed to `/tmp/amiguard-m22j-run`. AGTest contains
AmiGuard, the existing Probe helper and CLI scripts. AGFiles contains fixtures
and has `hard_drive_1_read_only = 1`; fixture host modes are 0444. ADF copies
are also 0444, with emulator floppy writes disabled. Only the known-clean
Workbench image was booted; synthetic bootblocks were inserted after startup.
The original profile was not edited. Actual settings and emulator identity
are retained in runtime.fs-uae, debug.uae and fs-uae.log.txt.

The initial attempt stopped because `/usr/bin/python3` (Python 3.14.4)
could not import Xlib. The runtime driver launches the GUI helper using
`sys.executable`, so the interpreter is exactly the same. The runtime-only fix
installed python-xlib 0.33 and six 1.17.0 under `/tmp/amiguard-m22j-python`:

```sh
/usr/bin/python3 -m pip install --no-cache-dir --target /tmp/amiguard-m22j-python python-xlib==0.33
PYTHONPATH=/tmp/amiguard-m22j-python /usr/bin/python3 -c 'import Xlib; print(Xlib.__file__)'
# /tmp/amiguard-m22j-python/Xlib/__init__.py
PYTHONPATH=/tmp/amiguard-m22j-python /usr/bin/python3 /tmp/amiguard-m22j-run/evidence/runtime-driver.py
```

No system or repository dependencies were changed. Before rerunning, old
logs and completion markers were archived under initial-blocked, so no stale
marker could pass a stage. The first GUI smoke action successfully captured
the active visible FS-UAE startup window. The existing GUI helper then typed
Execute commands into that window; all scans executed in the native Amiga
CLI. The driver's execute entry point was used, not its legacy build/prepare
function. The Xlib blocker is resolved.

## Commands and observed results

CLI scripts use DOS 1.2 redirection before arguments and then Type to display
the result, for example:

```text
AmiGuard >AGTest:positive.log FILE AGFiles:eicar.com.txt
Probe >AGTest:positive-probe.log
Type AGTest:positive.log
```

This is the mounted-path form of `AmiGuard FILE eicar.com.txt`.
All executed scripts are preserved under [commands](evidence/m2.2j/commands/).

| Input / command arguments | Actual result | Return code |
| --- | --- | --- |
| FILE AGFiles:eicar.com.txt | TEST-SIGNATURE: EICAR Standard Anti-Virus Test File (68 bytes) | 0 |
| FILE AGFiles:eicar-nearmiss.bin | NOT-HUNK: not an Amiga HUNK file (68 bytes) | 0 |
| FILE AGFiles:valid.hunk | VALID-HUNK: supported Amiga HUNK structure (40 bytes) | 0 |
| FILE AGFiles:plain.txt | NOT-HUNK: not an Amiga HUNK file (24 bytes) | 0 |
| FILE AGFiles:malformed.hunk | MALFORMED-HUNK: HUNK structure is malformed or unsupported (4 bytes) | 0 |
| FILE AGFiles:does-not-exist | ERROR: cannot open file read-only | 20 |
| FILE AGFiles:oversize.bin | ERROR: file exceeds 128 KiB M2.1 limit (131073 bytes) | 20 |
| DF0: — Workbench | STANDARD: Amiga DOS bootblock (valid checksum) | 0 |
| DF0: — valid-custom.adf | CUSTOM: custom bootblock (valid checksum) | 0 |
| DF0: — invalid.adf | UNKNOWN: Amiga DOS bootblock (invalid checksum) | 0 |
| DF0: — unknown.adf | UNKNOWN: unknown bootblock | 0 |

No scan output contains INFECTED. Near-miss and neutral cases contain no
TEST-SIGNATURE. The valid, plain, malformed and oversized fixtures are the
unchanged M2.2b fixtures. The missing path remained absent. Additional inherited
invalid-target and empty-drive tests also passed with controlled errors.

## Stability and read-only verification

EICAR **10/10** repeated scans returned the same exact TEST-SIGNATURE name and
return code 0, in addition to the initial EICAR scan. Free Chip RAM was
**351608 bytes before and after every repetition**, delta 0. No crash, hang,
Guru or progressive memory loss was observed. These are post-exit free-memory
measurements, not peak allocations. Near-miss, VALID-HUNK, NOT-HUNK and
MALFORMED-HUNK each also passed ten repetitions with the same stable free RAM.
STANDARD passed ten repeats; CUSTOM passed five repeats. The session remained
responsive and completed a final Workbench directory listing before normal quit.

All six fixture SHA-256 values were identical before launch and after the
session; this includes both EICAR files. All four ADF copies and all originals
(EICAR, ROM, Workbench and reference profile) also matched. Full before/after
values are in [manifest.json](evidence/m2.2j/manifest.json) and
[observations.json](evidence/m2.2j/observations.json), with additional assertions
and memory samples in [verified-results.json](evidence/m2.2j/verified-results.json).

## Evidence, deviations and validation

[Evidence directory](evidence/m2.2j/) contains native logs, per-scan return-code
and RAM probes, visually inspected screenshots, actual emulator configuration,
fixture preparation and execution scripts, dependency repair details and the
host check log. No EICAR fixture bytes, ROM, Workbench image or ADF binaries
are committed. Committed text copies have trailing whitespace removed; raw logs remain in the
disposable run. Emulator .uaem metadata sidecars are omitted.
Full disposable run remains at `/tmp/amiguard-m22j-run`.
The generic screenshot-review reminder in observations.json is supplemented
by the actual review recorded in verified-results.json.

After successful runtime completion, two Xlib BadWindow messages occurred
while releasing the quit chord after the emulator window closed. The driver
exited 0; this is the previously observed GUI shutdown behavior, not an
AmiGuard crash or a failed gate. No machine-profile deviation or runtime fix
was needed. Remaining blockers: none.

`make check`: PASS (five C suites, 73 Python tests and generated/metadata
checks). The signature-promotion rejection is an expected negative host test.
`git diff --check`: PASS before commit. Only this report and safe evidence
are included in the documentation commit on main. Final commit identity is
resolved with `git log -1 --format=%H -- docs/M2_2J_RUNTIME_QUALIFICATION.md`;
a commit cannot embed its own hash. Push and final clean status are reported
in the execution response.
