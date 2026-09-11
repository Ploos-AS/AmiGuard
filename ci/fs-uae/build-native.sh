#!/usr/bin/env bash
set -euo pipefail

IMAGE="${AMIGUARD_BEBBO_IMAGE:-amigadev/m68k-amigaos-gcc@sha256:b18080e6ffca8f793e0f539536a9138e9d2a548ca1a301c7483f43ee15fedfed}"
OUT="${1:-build/fs-uae/native}"
mkdir -p "$OUT"

docker pull "$IMAGE"
docker image inspect "$IMAGE" --format '{{join .RepoDigests "\n"}}' | tee "$OUT/toolchain-image.txt"

docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  "$IMAGE" \
  sh -lc 'make clean && make all CC=m68k-amigaos-gcc'

cp AmiGuard "$OUT/AmiGuard"
file "$OUT/AmiGuard" | tee "$OUT/file.txt"
sha256sum "$OUT/AmiGuard" | tee "$OUT/AmiGuard.sha256"

if ! grep -Eiq 'AmigaOS|Amiga.*executable|loadseg' "$OUT/file.txt"; then
  echo "ERROR: native output is not recognized as an Amiga executable" >&2
  exit 1
fi

printf 'STATUS=PASS\nGATE=NATIVE_BEBBO_BUILD\nIMAGE=%s\nBINARY=%s\n' "$IMAGE" "$OUT/AmiGuard" | tee "$OUT/result.txt"
