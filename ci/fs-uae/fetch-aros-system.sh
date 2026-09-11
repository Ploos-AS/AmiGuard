#!/usr/bin/env bash
set -euo pipefail

AROS_INDEX_URL="https://aros.sourceforge.io/cgi-bin/files?lang=en&type=nightly2"
AROS_TARGET="amiga-m68k-boot-iso"
OUT="${1:-build/fs-uae/aros-system}"
mkdir -p "$OUT"
index="$OUT/aros-nightly-index.html"

curl --fail --location --retry 3 --retry-delay 2 "$AROS_INDEX_URL" -o "$index"
url="$({ grep -oE 'href="[^"]*amiga-m68k-boot-iso[^"]*"' "$index" || true; } | head -n1 | sed -e 's/^href="//' -e 's/"$//' -e 's/&amp;/\&/g')"
[[ -n "$url" ]] || { echo "ERROR: could not resolve AROS nightly" >&2; exit 1; }
case "$url" in
  http://*|https://*) ;;
  //*) url="https:$url" ;;
  /*) url="https://aros.sourceforge.io$url" ;;
  *) url="https://aros.sourceforge.io/$url" ;;
esac
path="${url%%\?*}"
if [[ "$path" == */download ]]; then archive_name="$(basename "$(dirname "$path")")"; else archive_name="$(basename "$path")"; fi
[[ "$archive_name" == *"$AROS_TARGET"* ]] || { echo "ERROR: unexpected AROS target: $archive_name" >&2; exit 1; }
archive="$OUT/$archive_name"
curl --fail --location --retry 3 --retry-delay 2 "$url" -o "$archive"
sha256sum "$archive" | tee "$OUT/archive.sha256"
rm -rf "$OUT/archive-extracted"; mkdir -p "$OUT/archive-extracted"
case "$archive_name" in
  *.lha|*.LHA) lha xw="$OUT/archive-extracted" "$archive" >/dev/null ;;
  *.zip|*.ZIP) unzip -q "$archive" -d "$OUT/archive-extracted" ;;
  *) echo "ERROR: unsupported archive format" >&2; exit 1 ;;
esac
iso="$(find "$OUT/archive-extracted" -type f \( -iname '*.iso' -o -iname '*.ISO' \) -print -quit)"
[[ -n "$iso" ]] || { echo "ERROR: no ISO found" >&2; exit 1; }
cp "$iso" "$OUT/system.iso"
printf 'AROS_INDEX_URL=%s\nAROS_TARGET=%s\nAROS_ARCHIVE=%s\nAROS_URL=%s\nISO=%s\n' "$AROS_INDEX_URL" "$AROS_TARGET" "$archive_name" "$url" "$OUT/system.iso" >"$OUT/source.txt"
echo "$OUT/system.iso"
