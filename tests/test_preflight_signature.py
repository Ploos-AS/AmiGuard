import json
import os
import sys
import tempfile
import unittest

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import preflight_signature


class PreflightSignatureTests(unittest.TestCase):
    def write_json(self, directory, name, data):
        path = os.path.join(directory, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle)
        return path

    def valid_qualified(self):
        return {
            "schema": 1,
            "id": "synthetic-preflight-qualified",
            "name": "Synthetic Preflight Qualified",
            "family": "Synthetic",
            "kind": "bootblock",
            "status": "qualified",
            "synthetic": False,
            "source": {"reference": "unit test"},
            "provenance": {"method": "unit test"},
            "sample_sha256": "1" * 64,
            "signature": {"offset": 32, "bytes": "aabbccdd", "mask": "ffffffff"},
            "verifier": "none",
            "cleaner": "none",
        }

    def test_valid_qualified_draft_passes_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_json(directory, "draft.json", self.valid_qualified())
            before = set(os.listdir(directory))
            report = preflight_signature.preflight(path)
            after = set(os.listdir(directory))
            self.assertTrue(report["preflight_pass"])
            self.assertEqual(report["id"], "synthetic-preflight-qualified")
            self.assertFalse(report["qualified_compiled"])
            self.assertGreater(report["native_table_bytes_if_verified"],
                               report["native_table_bytes_without_qualified"])
            self.assertEqual(before, after)

    def test_research_draft_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            item = self.valid_qualified()
            item["status"] = "research"
            item["sample_sha256"] = None
            item["signature"] = None
            path = self.write_json(directory, "draft.json", item)
            with self.assertRaisesRegex(ValueError, "status=qualified"):
                preflight_signature.preflight(path)

    def test_verified_draft_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            item = self.valid_qualified()
            item["status"] = "verified"
            path = self.write_json(directory, "draft.json", item)
            with self.assertRaisesRegex(ValueError, "status=qualified"):
                preflight_signature.preflight(path)

    def test_invalid_qualified_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            item = self.valid_qualified()
            item["sample_sha256"] = "bad"
            path = self.write_json(directory, "draft.json", item)
            with self.assertRaisesRegex(ValueError, "sample_sha256"):
                preflight_signature.preflight(path)

    def test_duplicate_repository_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            item = self.valid_qualified()
            item["id"] = "amiguard.test.marker"
            path = self.write_json(directory, "draft.json", item)
            with self.assertRaisesRegex(ValueError, "already exists"):
                preflight_signature.preflight(path)


if __name__ == "__main__":
    unittest.main()
