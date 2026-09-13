#!/usr/bin/env bash
set -euo pipefail

IMAGE="${AMIGUARD_BEBBO_IMAGE:-amigadev/m68k-amigaos-gcc@sha256:b18080e6ffca8f793e0f539536a9138e9d2a548ca1a301c7483f43ee15fedfed}"
OUT="${1:-build/fs-uae/native}"
mkdir -p "$OUT"

docker pull "$IMAGE"
docker image inspect "$IMAGE" --format '{{join .RepoDigests "\n"}}' | tee "$OUT/toolchain-image.txt"

# The pinned Bebbo image contains the cross compiler but not make.
# Keep this source set and flags aligned with the repository Makefile.
rm -f AmiGuard
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  "$IMAGE" \
  m68k-amigaos-gcc \
    -Isrc \
    -DAMIGUARD_NATIVE_XVS=1 \
    -O2 -Wall -Wextra -Werror \
    -m68000 -mcrt=nix13 \
    -o AmiGuard \
    src/main.c \
    src/scanner.c \
    src/signatures.c \
    src/trackdisk.c \
    src/hunk.c \
    src/file_intake.c \
    src/file_signatures.c \
    src/xvs_bridge.c

cp AmiGuard "$OUT/AmiGuard"
file "$OUT/AmiGuard" | tee "$OUT/file.txt"
sha256sum "$OUT/AmiGuard" | tee "$OUT/AmiGuard.sha256"

if ! grep -Eiq 'AmigaOS|Amiga.*executable|loadseg' "$OUT/file.txt"; then
  echo "ERROR: native output is not recognized as an Amiga executable" >&2
  exit 1
fi

printf 'STATUS=PASS\nGATE=NATIVE_BEBBO_BUILD\nIMAGE=%s\nBINARY=%s\n' "$IMAGE" "$OUT/AmiGuard" | tee "$OUT/result.txt"
