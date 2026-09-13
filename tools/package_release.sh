#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.0}"
ROOT="AmiGuard-v${VERSION}"
DIST="dist"
STAGE="${DIST}/${ROOT}"
AMINET_ROOT="AmiGuard"
AMINET_STAGE="${DIST}/${AMINET_ROOT}"

if [[ ! -f AmiGuard ]]; then
  echo "ERROR: native AmiGuard binary not found; build it first" >&2
  exit 1
fi

rm -rf "$STAGE" "$AMINET_STAGE"
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

rm -f "${DIST}/${ROOT}.zip" "${DIST}/${ROOT}.zip.sha256" \
  "${DIST}/AmiGuard.lha" "${DIST}/AmiGuard.lha.sha256" \
  "${DIST}/AmiGuard.readme"
(
  cd "$DIST"
  zip -qr "${ROOT}.zip" "$ROOT"
)
sha256sum "${DIST}/${ROOT}.zip" > "${DIST}/${ROOT}.zip.sha256"

# Aminet package layout: AmiGuard.lha + sibling AmiGuard.readme.
# Copy only redistributable release payload; do not include proprietary xvs.library.
mkdir -p "$AMINET_STAGE/docs"
cp "$STAGE/AmiGuard" "$AMINET_STAGE/AmiGuard"
cp "$STAGE/README.md" "$STAGE/LICENSE" "$STAGE/RELEASE.txt" "$AMINET_STAGE/"
cp "$STAGE/docs/SAMPLE_SUBMISSION.md" "$STAGE/docs/M2_3_XVS_BRIDGE.md" \
  "$STAGE/docs/V0_1_0_NATIVE_QUALIFICATION.md" "$AMINET_STAGE/docs/"
cp "$STAGE/AmiGuard.readme" "${DIST}/AmiGuard.readme"

LHA_CREATOR=""
for candidate in lha lharc; do
  if ! command -v "$candidate" >/dev/null 2>&1; then
    continue
  fi
  if "$candidate" --version 2>&1 | grep -qi 'lhasa'; then
    continue
  fi
  LHA_CREATOR="$candidate"
  break
done

if [[ -z "$LHA_CREATOR" ]]; then
  cat >&2 <<'EOF'
ERROR: Aminet release requires an LHA archive creator.
The installed /usr/bin/lha is Lhasa, which is extract-only and cannot create
AmiGuard.lha. Install a real LHA/LHArc-compatible archiver, then rerun:
  tools/package_release.sh 0.1.0
ZIP output has been created, but packaging is intentionally FAIL until the
Aminet AmiGuard.lha + AmiGuard.readme pair can be produced.
EOF
  exit 2
fi

(
  cd "$DIST"
  "$LHA_CREATOR" -aq "AmiGuard.lha" "$AMINET_ROOT"
)
sha256sum "${DIST}/AmiGuard.lha" > "${DIST}/AmiGuard.lha.sha256"
rm -rf "$AMINET_STAGE"

printf 'Release packages created in %s\n' "$DIST"
printf '  %s\n' "${DIST}/${ROOT}.zip"
printf '  %s\n' "${DIST}/${ROOT}.zip.sha256"
printf '  %s\n' "${DIST}/AmiGuard.lha"
printf '  %s\n' "${DIST}/AmiGuard.lha.sha256"
printf '  %s\n' "${DIST}/AmiGuard.readme"
