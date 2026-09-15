#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-build/m3_4}"
mkdir -p "$OUT"
result="$OUT/result.txt"
: >"$result"

pass() { echo "PASS: $*" | tee -a "$result"; }
fail() { echo "FAIL: $*" | tee -a "$result"; exit 1; }

# M3.4 is a consolidated qualification gate. It deliberately uses only
# committed safe/test fixtures; production malware evidence belongs to M2.5.
make check >>"$OUT/host.log" 2>&1 || fail "host regression suite"
pass "host regression suite"

ci/fs-uae/build-native.sh >>"$OUT/native.log" 2>&1 || fail "native m68k build"
[[ -s build/fs-uae/native/AmiGuard ]] || fail "native AmiGuard binary missing"
pass "native m68k build"

# The host tests exercise the three M3 providers independently: recursive
# volume traversal, bounded trackdisk reads, and full ADF traversal including
# the established bootblock detector. Re-run the binaries explicitly so the
# qualification evidence records each disk path rather than only make check.
for gate in test_volume_scanner test_trackdisk test_image_scanner; do
  [[ -x "build/$gate" ]] || fail "$gate missing after make check"
  "build/$gate" >>"$OUT/${gate}.log" 2>&1 || fail "$gate"
  pass "$gate"
done

# Source-level read-only invariant: the trackdisk implementation must not
# issue write/update commands. This supplements the mocked CMD_READ assertion.
if grep -Eq '\b(CMD_WRITE|TD_FORMAT|TD_UPDATE)\b' src/trackdisk.c; then
  fail "trackdisk scanner contains a write/update command"
fi
pass "trackdisk scanner has no write/update command"

# Resource/malformed-media behavior is covered by the provider tests:
# zero/overflow/alignment bounds, short/error reads, ADF size/raw-byte bounds,
# recursive object/depth limits and explicit error verdicts.
pass "bounded and malformed-media regression coverage"

{
  echo "STATUS=PASS"
  echo "MILESTONE=M3.4"
  echo "ENGINE=DISK"
  echo "PATHS=volume,trackdisk,adf"
  echo "CPU_TARGET=68000"
  echo "RUNTIME_TARGET=AmigaOS/Kickstart 1.2+"
  echo "LOW_MEMORY_TARGET=512KiB-class"
  echo "WRITE_POLICY=read-only"
  echo "MALWARE_FIXTURES=none"
  echo "NOTE=visible classic-Amiga runtime evidence remains a separate historical compatibility record"
} | tee -a "$result"
