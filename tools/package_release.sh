#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.0-rc1}"
ROOT="AmiGuard-v${VERSION}"
DIST="dist"
STAGE="${DIST}/${ROOT}"

if [[ ! -f AmiGuard ]]; then
  echo "ERROR: native AmiGuard binary not found; build it first" >&2
  exit 1
fi

rm -rf "$STAGE"
mkdir -p "$STAGE/docs"

cp AmiGuard "$STAGE/AmiGuard"
cp README.md LICENSE "$STAGE/"
cp docs/SAMPLE_SUBMISSION.md "$STAGE/docs/"
cp docs/M2_3_XVS_BRIDGE.md "$STAGE/docs/"

cat > "$STAGE/RELEASE.txt" <<EOF
AmiGuard v${VERSION}

Target: AmigaOS / Kickstart 1.2+ / Motorola 68000

This release candidate includes AmiGuard's native scanner plus optional,
transitional xvs.library integration. xvs.library is not bundled and is not
required. xvs-only detections are reported as XVS-DETECTED, never INFECTED.

Please submit authentic suspicious files or complete Amiga disk images at:
https://amiguard.ploos.no/

See README.md and docs/SAMPLE_SUBMISSION.md for what to submit and why.
EOF

(
  cd "$STAGE"
  sha256sum AmiGuard README.md LICENSE RELEASE.txt docs/SAMPLE_SUBMISSION.md docs/M2_3_XVS_BRIDGE.md > SHA256SUMS
)

rm -f "${DIST}/${ROOT}.zip" "${DIST}/${ROOT}.lha"
(
  cd "$DIST"
  zip -qr "${ROOT}.zip" "$ROOT"
)

if command -v lha >/dev/null 2>&1; then
  (
    cd "$DIST"
    lha -aq "${ROOT}.lha" "$ROOT"
  )
fi

sha256sum "${DIST}/${ROOT}.zip" > "${DIST}/${ROOT}.zip.sha256"
if [[ -f "${DIST}/${ROOT}.lha" ]]; then
  sha256sum "${DIST}/${ROOT}.lha" > "${DIST}/${ROOT}.lha.sha256"
fi

printf 'Release candidate package created in %s\n' "$DIST"
