import json
import os
import stat
import tempfile
import unittest

from tools import extract_clean_adf_corpus as tool


class ExtractCleanAdfCorpusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = self.temp.name

    def write(self, rel, data):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def fake_xdftool(self):
        path = os.path.join(self.root, "xdftool")
        script = """#!/usr/bin/env python3
import os, sys
adf, command, outdir = sys.argv[1:4]
if command != 'unpack':
    sys.exit(9)
os.makedirs(os.path.join(outdir, 'C'), exist_ok=True)
with open(os.path.join(outdir, 'C', 'List'), 'wb') as h:
    h.write(b'clean-program')
with open(os.path.join(outdir, 'S-startup'), 'wb') as h:
    h.write(b'echo clean')
"""
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(script)
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
        return path

    def test_collect_files_hashes_and_paths(self):
        root = os.path.join(self.root, "out")
        os.makedirs(os.path.join(root, "C"))
        path = os.path.join(root, "C", "List")
        with open(path, "wb") as handle:
            handle.write(b"abc")
        entries = tool.collect_files(root, 1, "/tmp/source.adf", "a" * 64)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["internal_path"], "C/List")
        self.assertEqual(entries[0]["size"], 3)
        self.assertEqual(entries[0]["sha256"],
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_build_manifest_preserves_source_and_records_files(self):
        adf = self.write("disk.adf", b"DOS\0" + b"x" * 1024)
        before = tool.sha256_file(adf)
        output = os.path.join(self.root, "corpus")
        manifest = tool.build_manifest([adf], output, self.fake_xdftool())
        self.assertEqual(tool.sha256_file(adf), before)
        self.assertEqual(manifest["kind"], "amiguard-clean-file-corpus")
        self.assertEqual(manifest["source_count"], 1)
        self.assertEqual(manifest["file_count"], 2)
        self.assertTrue(manifest["sources"][0]["read_only_integrity_pass"])
        self.assertEqual(sorted(x["internal_path"] for x in manifest["files"]),
                         ["C/List", "S-startup"])

    def test_missing_xdftool_fails(self):
        with self.assertRaises(ValueError):
            tool.build_manifest([], os.path.join(self.root, "out"),
                                os.path.join(self.root, "missing-xdftool"))

    def test_cli_writes_manifest(self):
        adf = self.write("disk2.adf", b"DOS\1" + b"z" * 1024)
        output = os.path.join(self.root, "corpus2")
        manifest_path = os.path.join(self.root, "manifest.json")
        rc = tool.main([
            adf,
            "--output-dir", output,
            "--manifest", manifest_path,
            "--xdftool", self.fake_xdftool(),
        ])
        self.assertEqual(rc, 0)
        with open(manifest_path, "r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        self.assertEqual(manifest["file_count"], 2)


if __name__ == "__main__":
    unittest.main()
