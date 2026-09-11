#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/build/fs-uae/boot"
CONFIG="$ROOT/ci/fs-uae/aros-smoke.fs-uae"
mkdir -p "$OUT"

fs-uae --version >"$OUT/fs-uae-version.txt" 2>&1
set +e
timeout --signal=TERM 20s xvfb-run -a fs-uae "$CONFIG" >"$OUT/fs-uae.log" 2>&1
rc=$?
set -e

if [[ $rc -ne 124 ]]; then
  printf 'STATUS=FAIL\nGATE=AROS_BOOT_SMOKE\nFS_UAE_EXIT=%s\n' "$rc" | tee "$OUT/result.txt"
  cat "$OUT/fs-uae.log"
  exit 1
fi

printf 'STATUS=PASS\nGATE=AROS_BOOT_SMOKE\nMODEL=A1200\nKICKSTART=internal\nOBSERVATION=emulator_remained_running_for_20_seconds\n' | tee "$OUT/result.txt"
