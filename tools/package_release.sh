#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.0}"
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
cp docs/V0_1_0_NATIVE_QUALIFICATION.md "$STAGE/docs/"

cat > "$STAGE/RELEASE.txt" <<EOF
AmiGuard v${VERSION}

Copyright: Ploos AS
Uploader: Per Gustav Ousdal
Contact: amiguard@ousdal.org
License: MIT
Target: AmigaOS / Kickstart 1.2+ / Motorola 68000

AmiGuard is an open-source antivirus project for classic Amiga systems.
This release includes native bootblock and file scanning plus optional,
transitional xvs.library integration. xvs.library is not bundled and is not
required. xvs-only detections are reported as XVS-DETECTED, never INFECTED.

Please submit authentic suspicious files or complete Amiga disk images at:
https://amiguard.ploos.no/

Useful submissions include suspicious executables, infected or suspicious ADF
images, bootblock samples, and files reported by another Amiga antivirus. A
complete disk image is preferred when practical because it preserves the
bootblock and surrounding context.

See README.md and docs/SAMPLE_SUBMISSION.md for what to submit, safe handling,
and why community samples are important to building independent AmiGuard
signatures.
EOF

cat > "$STAGE/AmiGuard.readme" <<EOF
Short:        Open-source antivirus for classic Amiga systems
Uploader:     Per Gustav Ousdal
Contact:      amiguard@ousdal.org
Author:       Ploos AS
Type:         util/virus
Version:      ${VERSION}
Architecture: m68k-amigaos
Requires:     AmigaOS/Kickstart 1.2+, Motorola 68000
License:      MIT

AmiGuard is an open-source antivirus for classic Amiga systems. It scans
bootblocks and files read-only and targets AmigaOS/Kickstart 1.2+ on 68000.

The optional xvs.library bridge is transitional and is not bundled. Results
reported only by xvs.library are labelled XVS-DETECTED and are not presented
as independently verified AmiGuard INFECTED verdicts.

Community malware samples are important to AmiGuard. If you have an authentic
suspicious Amiga executable, infected/suspicious ADF, bootblock sample, or a
file detected by another Amiga antivirus, please submit the original material
at https://amiguard.ploos.no/ so it can be independently analysed and used to
build qualified AmiGuard signatures.

Copyright (c) 2026 Ploos AS
EOF

(
  cd "$STAGE"
  sha256sum AmiGuard README.md LICENSE RELEASE.txt AmiGuard.readme \
    docs/SAMPLE_SUBMISSION.md docs/M2_3_XVS_BRIDGE.md \
    docs/V0_1_0_NATIVE_QUALIFICATION.md > SHA256SUMS
)

rm -f "${DIST}/${ROOT}.zip" "${DIST}/${ROOT}.lha" \
  "${DIST}/${ROOT}.zip.sha256" "${DIST}/${ROOT}.lha.sha256"
(
  cd "$DIST"
  zip -qr "${ROOT}.zip" "$ROOT"
)

# Ubuntu's /usr/bin/lha is commonly Lhasa, which can extract but cannot create
# LHA archives. Treat that as an unavailable creator rather than a packaging
# failure. A real LHA-capable implementation will still be used when present.
LHA_CAN_CREATE=0
if command -v lha >/dev/null 2>&1; then
  if lha --version 2>&1 | grep -qi 'lhasa'; then
    printf 'NOTE: lha is Lhasa (extract-only); skipping .lha creation\n' >&2
  else
    LHA_CAN_CREATE=1
  fi
fi

if [[ "$LHA_CAN_CREATE" -eq 1 ]]; then
  if (
    cd "$DIST"
    lha -aq "${ROOT}.lha" "$ROOT"
  ); then
    sha256sum "${DIST}/${ROOT}.lha" > "${DIST}/${ROOT}.lha.sha256"
  else
    rm -f "${DIST}/${ROOT}.lha" "${DIST}/${ROOT}.lha.sha256"
    printf 'WARNING: installed lha could not create an archive; continuing with ZIP\n' >&2
  fi
fi

sha256sum "${DIST}/${ROOT}.zip" > "${DIST}/${ROOT}.zip.sha256"

printf 'Release package created in %s\n' "$DIST"
printf '  %s\n' "${DIST}/${ROOT}.zip"
printf '  %s\n' "${DIST}/${ROOT}.zip.sha256"
if [[ -f "${DIST}/${ROOT}.lha" ]]; then
  printf '  %s\n' "${DIST}/${ROOT}.lha"
  printf '  %s\n' "${DIST}/${ROOT}.lha.sha256"
fi
