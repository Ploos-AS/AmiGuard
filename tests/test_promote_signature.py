#!/usr/bin/env python3
import importlib.util
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
SPEC = importlib.util.spec_from_file_location(
    "promote_signature", os.path.join(TOOLS, "promote_signature.py"))
PROMOTE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROMOTE)


class PromoteSignatureTests(unittest.TestCase):
    def make_file(self, directory, name, data):
        path = os.path.join(directory, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def make_manifest(self, path, clean_path, clean_hash):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({
                "schema": 1,
                "kind": "amiguard-clean-bootblock-corpus",
                "entries": [{
                    "path": clean_path,
                    "bootblock_sha256": clean_hash,
                }],
            }, handle)

    def test_build_verified_after_pass(self):
        report = {
            "qualified": True,
            "sample_bootblock_sha256": "a" * 64,
            "offset": 12,
            "pattern": "aabbcc",
            "mask": "ffffff",
            "clean_results": [{"path": "/clean"}],
        }
        item = PROMOTE.build_verified(
            report, "virus.test", "Virus Test", "TestFamily", "source",
            "derived independently", "none", "none")
        self.assertEqual(item["status"], "verified")
        self.assertFalse(item["synthetic"])
        self.assertEqual(item["sample_sha256"], "a" * 64)
        self.assertEqual(item["signature"]["offset"], 12)
        self.assertEqual(item["signature"]["bytes"], "aabbcc")
        self.assertEqual(item["signature"]["mask"], "ffffff")
        self.assertEqual(item["provenance"]["clean_entries_tested"], 1)

    def test_rejects_failed_qualification(self):
        with self.assertRaises(ValueError):
            PROMOTE.build_verified(
                {"qualified": False}, "virus.test", "Virus Test", "TestFamily",
                "source", "note", "none", "none")

    def test_cli_refuses_clean_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            sample = bytearray(1024)
            clean = bytearray(1024)
            sample[20:24] = b"TEST"
            clean[20:24] = b"TEST"
            sample_path = self.make_file(directory, "sample.adf", sample)
            clean_path = self.make_file(directory, "clean.adf", clean)
            clean_hash = PROMOTE.qualify_signature.sha256(bytes(clean))
            manifest = os.path.join(directory, "clean.json")
            self.make_manifest(manifest, clean_path, clean_hash)
            rc = PROMOTE.main([
                sample_path,
                "--clean-manifest", manifest,
                "--offset", "20",
                "--pattern", "54455354",
                "--mask", "ffffffff",
                "--id", "virus.test",
                "--name", "Virus Test",
                "--family", "TestFamily",
                "--source", "test source",
                "--provenance-note", "test note",
            ])
            self.assertEqual(rc, 1)

    def test_cli_writes_verified_draft_after_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            sample = bytearray(1024)
            clean = bytearray(1024)
            sample[20:24] = b"TEST"
            clean[20:24] = b"SAFE"
            sample_path = self.make_file(directory, "sample.adf", sample)
            clean_path = self.make_file(directory, "clean.adf", clean)
            clean_hash = PROMOTE.qualify_signature.sha256(bytes(clean))
            manifest = os.path.join(directory, "clean.json")
            output = os.path.join(directory, "verified.json")
            self.make_manifest(manifest, clean_path, clean_hash)
            rc = PROMOTE.main([
                sample_path,
                "--clean-manifest", manifest,
                "--offset", "20",
                "--pattern", "54455354",
                "--mask", "ffffffff",
                "--id", "virus.test",
                "--name", "Virus Test",
                "--family", "TestFamily",
                "--source", "test source",
                "--provenance-note", "test note",
                "-o", output,
            ])
            self.assertEqual(rc, 0)
            with open(output, "r", encoding="utf-8") as handle:
                item = json.load(handle)
            self.assertEqual(item["status"], "verified")
            self.assertEqual(item["signature"]["bytes"], "54455354")


if __name__ == "__main__":
    unittest.main()
