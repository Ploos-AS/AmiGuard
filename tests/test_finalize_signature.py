import json
import os
import sys
import tempfile
import unittest

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import finalize_signature


class FinalizeSignatureTests(unittest.TestCase):
    def valid_qualified(self):
        return {
            "schema": 1,
            "id": "virus.runtime.test",
            "name": "Virus Runtime Test",
            "family": "TestFamily",
            "kind": "bootblock",
            "status": "qualified",
            "synthetic": False,
            "source": {"reference": "unit test"},
            "provenance": {"method": "unit test"},
            "sample_sha256": "2" * 64,
            "signature": {"offset": 16, "bytes": "aabb", "mask": "ffff"},
            "verifier": "none",
            "cleaner": "none",
        }

    def valid_evidence(self):
        return {
            "result": "pass",
            "platform": "visible FS-UAE A500",
            "os": "Kickstart 1.2 / Workbench 1.2",
            "cpu": "Motorola 68000",
            "evidence": "signature detected expected isolated fixture; clean regressions passed",
        }

    def test_finalize_passes_and_preserves_signature(self):
        item = finalize_signature.finalize(self.valid_qualified(), self.valid_evidence())
        self.assertEqual(item["status"], "verified")
        self.assertEqual(item["signature"]["bytes"], "aabb")
        self.assertEqual(item["sample_sha256"], "2" * 64)
        self.assertEqual(item["provenance"]["runtime_verification"]["result"], "pass")

    def test_non_qualified_rejected(self):
        item = self.valid_qualified()
        item["status"] = "verified"
        with self.assertRaisesRegex(ValueError, "status=qualified"):
            finalize_signature.finalize(item, self.valid_evidence())

    def test_failed_runtime_rejected(self):
        evidence = self.valid_evidence()
        evidence["result"] = "fail"
        with self.assertRaisesRegex(ValueError, "result=pass"):
            finalize_signature.finalize(self.valid_qualified(), evidence)

    def test_missing_runtime_field_rejected(self):
        evidence = self.valid_evidence()
        evidence.pop("cpu")
        with self.assertRaisesRegex(ValueError, "requires cpu"):
            finalize_signature.finalize(self.valid_qualified(), evidence)


if __name__ == "__main__":
    unittest.main()
