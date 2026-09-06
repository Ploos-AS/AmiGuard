#!/usr/bin/env python3
import importlib.util
import json
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE_PATH = os.path.join(ROOT, "tools", "qualify_signature.py")
spec = importlib.util.spec_from_file_location("qualify_signature", MODULE_PATH)
qual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qual)


class QualifySignatureTests(unittest.TestCase):
    def write_file(self, directory, name, data):
        path = os.path.join(directory, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def test_positive_and_clean_negative_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample = bytearray(1024)
            sample[100:104] = bytes.fromhex("a1b2c3d4")
            clean = bytearray(1024)
            sample_path = self.write_file(tmp, "sample.adf", bytes(sample))
            clean_path = self.write_file(tmp, "clean.adf", bytes(clean))
            manifest = os.path.join(tmp, "clean.json")
            with open(manifest, "w", encoding="utf-8") as handle:
                json.dump({"schema": 1, "entries": [{"path": clean_path}]}, handle)
            report = qual.qualify(sample_path, manifest, 100, "a1b2c3d4", "ffffffff")
            self.assertTrue(report["positive_match"])
            self.assertTrue(report["clean_regression_pass"])
            self.assertTrue(report["qualified"])

    def test_clean_false_positive_blocks_qualification(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = bytearray(1024)
            data[100:104] = bytes.fromhex("a1b2c3d4")
            sample_path = self.write_file(tmp, "sample.adf", bytes(data))
            clean_path = self.write_file(tmp, "clean.adf", bytes(data))
            manifest = os.path.join(tmp, "clean.json")
            with open(manifest, "w", encoding="utf-8") as handle:
                json.dump({"schema": 1, "entries": [{"path": clean_path}]}, handle)
            report = qual.qualify(sample_path, manifest, 100, "a1b2c3d4", "ffffffff")
            self.assertFalse(report["clean_regression_pass"])
            self.assertFalse(report["qualified"])

    def test_masked_match(self):
        data = bytearray(1024)
        data[20:24] = bytes.fromhex("a1bfc3d4")
        self.assertTrue(qual.match_signature(bytes(data), 20,
                                             bytes.fromhex("a1b2c3d4"),
                                             bytes.fromhex("fff0ffff")))


if __name__ == "__main__":
    unittest.main()
