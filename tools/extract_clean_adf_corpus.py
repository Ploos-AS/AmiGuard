#!/usr/bin/env python3
"""Extract a local clean-file corpus from trusted ADF images using xdftool.

ADF inputs are treated as immutable source artifacts. The tool records each
source image SHA-256 before extraction, invokes amitools' xdftool in read-only
unpack mode, verifies the source hash again afterwards, and emits a manifest of
regular extracted files with provenance and SHA-256 hashes.

No ADF or extracted third-party file is copied into the AmiGuard repository by
this tool.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(index, path):
    base = os.path.basename(path)
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in base)
    return "%02d-%s" % (index, cleaned)


def collect_files(root, source_index, source_path, source_sha256):
    entries = []
    root_real = os.path.realpath(root)
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(current, d))]
        for name in sorted(files):
            path = os.path.join(current, name)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            real = os.path.realpath(path)
            if real != root_real and not real.startswith(root_real + os.sep):
                raise ValueError("extracted path escapes output directory")
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            entries.append({
                "source_index": source_index,
                "source_adf": os.path.abspath(source_path),
                "source_adf_sha256": source_sha256,
                "internal_path": rel,
                "extracted_path": os.path.abspath(path),
                "size": os.path.getsize(path),
                "sha256": sha256_file(path),
            })
    entries.sort(key=lambda item: (item["source_index"], item["internal_path"]))
    return entries


def extract_one(xdftool, adf, out_dir):
    proc = subprocess.run(
        [xdftool, adf, "unpack", out_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "xdftool failed"
        raise ValueError("%s: %s" % (adf, detail))


def build_manifest(adfs, output_dir, xdftool="xdftool"):
    resolved = shutil.which(xdftool) if os.path.sep not in xdftool else xdftool
    if not resolved or not os.path.isfile(resolved) or not os.access(resolved, os.X_OK):
        raise ValueError("xdftool not found; install amitools or pass --xdftool")

    os.makedirs(output_dir, exist_ok=True)
    sources = []
    files = []
    seen_hashes = {}

    for index, adf in enumerate(adfs, 1):
        adf = os.path.abspath(adf)
        if not os.path.isfile(adf):
            raise ValueError("ADF not found: %s" % adf)
        before = sha256_file(adf)
        target = os.path.join(output_dir, safe_name(index, adf))
        if os.path.exists(target):
            raise ValueError("output already exists: %s" % target)
        os.makedirs(target)
        extract_one(resolved, adf, target)
        after = sha256_file(adf)
        if before != after:
            raise ValueError("source ADF changed during extraction: %s" % adf)

        source_files = collect_files(target, index, adf, before)
        sources.append({
            "index": index,
            "path": adf,
            "size": os.path.getsize(adf),
            "sha256": before,
            "read_only_integrity_pass": True,
            "files_extracted": len(source_files),
        })
        files.extend(source_files)

    for entry in files:
        digest = entry["sha256"]
        seen_hashes.setdefault(digest, []).append(entry["extracted_path"])

    duplicate_groups = [
        {"sha256": digest, "paths": paths}
        for digest, paths in sorted(seen_hashes.items()) if len(paths) > 1
    ]

    return {
        "schema": 1,
        "kind": "amiguard-clean-file-corpus",
        "trust": "operator-selected trusted-source clean candidates",
        "extraction_tool": "amitools xdftool",
        "source_count": len(sources),
        "file_count": len(files),
        "sources": sources,
        "files": files,
        "duplicate_groups": duplicate_groups,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract a read-only AmiGuard clean-file corpus from trusted ADF images")
    parser.add_argument("adfs", nargs="+")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--xdftool", default="xdftool")
    args = parser.parse_args(argv)

    try:
        manifest = build_manifest(args.adfs, args.output_dir, args.xdftool)
        with open(args.manifest, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except (OSError, ValueError) as exc:
        print("ADF clean-corpus extractor: %s" % exc, file=sys.stderr)
        return 1

    print("Extracted %d files from %d ADFs" %
          (manifest["file_count"], manifest["source_count"]))
    print("Manifest: %s" % args.manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
