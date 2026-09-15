#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-build/fs-uae/aros-guest}"
SYSTEM="build/fs-uae/aros-system"
mkdir -p "$OUT"
[[ -f build/fs-uae/native/AmiGuard ]] || { echo "ERROR: native AmiGuard binary missing" >&2; exit 1; }

iso="$(ci/fs-uae/fetch-aros-system.sh "$SYSTEM" | tail -n1)"
root="$OUT/system-root"
rm -rf "$root"; mkdir -p "$root"
7z x -y -o"$root" "$iso" >/dev/null
startup="$(find "$root" -type f -ipath '*/s/startup-sequence' -print -quit)"
[[ -n "$startup" ]] || { echo "ERROR: AROS ISO lacks S/Startup-Sequence" >&2; exit 1; }
aros_root="$(dirname "$(dirname "$startup")")"
cp build/fs-uae/native/AmiGuard "$aros_root/AmiGuard"
cp "$startup" "$startup.amiguard-original"

# Harmless synthetic detector fixture: four prefix bytes followed by the
# committed test-only AmiGuard marker at offset 4. No malware is used in CI.
printf 'SAFEAMIGUARD-FILE-TEST' >"$aros_root/amiguard-ci-fixture.bin"

cat >"$startup" <<'EOF'
SYS:C/Echo "AMIGUARD_CI_GUEST_STARTED=1" >SYS:amiguard-ci-started.txt
SYS:AmiGuard FILE SYS:amiguard-ci-fixture.bin >SYS:amiguard-ci-output.txt
SYS:C/Echo $RC >SYS:amiguard-ci-rc.txt
SYS:C/Echo "AMIGUARD_CI_GUEST_DONE=1" >SYS:amiguard-ci-done.txt
SYS:C/Execute SYS:S/Startup-Sequence.amiguard-original
EOF

config="$OUT/aros-guest.fs-uae"
sed "s|@AROS_ROOT@|$PWD/$aros_root|" ci/fs-uae/aros-guest.fs-uae >"$config"
fs-uae --version >"$OUT/fs-uae-version.txt" 2>&1 || true

# FS-UAE is an interactive emulator and normally keeps running after the
# detector has finished. Run it in the background, observe the host-mounted
# evidence files, and terminate the emulator as soon as the guest gate is done.
# This avoids making every successful qualification wait for the hard timeout.
set +e
xvfb-run -a fs-uae "$config" >"$OUT/fs-uae.log" 2>&1 &
emu_pid=$!
set -e

finished=0
for _ in $(seq 1 45); do
  if [[ -f "$aros_root/amiguard-ci-done.txt" ]]; then
    finished=1
    break
  fi
  if ! kill -0 "$emu_pid" 2>/dev/null; then
    break
  fi
  sleep 1
done

if kill -0 "$emu_pid" 2>/dev/null; then
  kill "$emu_pid" 2>/dev/null || true
  for _ in $(seq 1 5); do
    kill -0 "$emu_pid" 2>/dev/null || break
    sleep 1
  done
  kill -KILL "$emu_pid" 2>/dev/null || true
fi
set +e
wait "$emu_pid"
rc=$?
set -e

status=FAIL
observation=guest_result_missing
out="$aros_root/amiguard-ci-output.txt"
guest_rc="$aros_root/amiguard-ci-rc.txt"
if [[ "$finished" == 1 ]] && [[ -f "$out" ]] && grep -q 'TEST-SIGNATURE: AmiGuard synthetic file test marker' "$out"; then
  status=PASS
  observation=guest_executed_amiguard_and_detected_synthetic_fixture
elif [[ -f "$out" ]]; then
  observation=guest_executed_amiguard_but_expected_test_signature_missing
fi

{
  echo "STATUS=$status"
  echo "GATE=AROS_GUEST_DETECTOR_EXECUTION"
  echo "MODEL=A1200"
  echo "KICKSTART=internal"
  echo "QUALIFICATION=provisional-ci-only"
  echo "FS_UAE_EXIT=$rc"
  echo "GUEST_DONE=$finished"
  echo "OBSERVATION=$observation"
  [[ -f "$guest_rc" ]] && tr -d '\r' <"$guest_rc" | sed 's/^/GUEST_RC=/'
  [[ -f "$out" ]] && tr -d '\r' <"$out" | sed 's/^/GUEST_OUTPUT=/'
} | tee "$OUT/result.txt"

[[ "$status" == PASS ]]
