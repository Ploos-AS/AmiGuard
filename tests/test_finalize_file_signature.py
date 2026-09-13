import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "finalize_file_signature.py"


def qualified():
    return {
        "schema": 1,
        "id": "fixture-virus",
        "name": "Fixture Virus",
        "family": "Fixture",
        "kind": "file",
        "status": "qualified",
        "synthetic": False,
        "source": {"description": "synthetic test source"},
        "provenance": {"description": "synthetic test provenance"},
        "sample_sha256": "a" * 64,
        "signature": {"offset": 8, "bytes": "0011223344556677", "mask": "ffffffffffffffff"},
        "verifier": "manual-sample-backed-verifier",
        "cleaner": "none",
        "candidate_is_verified_signature": False,
        "malware_claim": False,
        "native_activation": False,
        "requires_visible_native_runtime": True,
    }


def evidence():
    return {
        "result": "pass",
        "signature_id": "fixture-virus",
        "sample_sha256": "a" * 64,
        "platform": "FS-UAE A500",
        "os": "Kickstart/Workbench 1.2",
        "cpu": "68000",
        "evidence": "visible native qualification fixture",
    }


class FinalizeFileSignatureTests(unittest.TestCase):
    def run_tool(self, item=None, ev=None):
        with tempfile.TemporaryDirectory() as td:
            qp = Path(td) / "qualified.json"
            ep = Path(td) / "evidence.json"
            qp.write_text(json.dumps(item or qualified()))
            ep.write_text(json.dumps(ev or evidence()))
            return subprocess.run([
                "python3", str(TOOL), str(qp), "--runtime-evidence", str(ep)
            ], capture_output=True, text=True)

    def test_emits_verified_file_signature(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "verified")
        self.assertEqual(data["kind"], "file")
        self.assertEqual(data["provenance"]["runtime_verification"]["result"], "pass")
        self.assertNotIn("candidate_is_verified_signature", data)
        self.assertNotIn("native_activation", data)

    def test_rejects_non_qualified_input(self):
        item = qualified()
        item["status"] = "research"
        item["sample_sha256"] = None
        item["signature"] = None
        result = self.run_tool(item=item)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires status=qualified", result.stderr)

    def test_rejects_failed_native_evidence(self):
        ev = evidence()
        ev["result"] = "fail"
        result = self.run_tool(ev=ev)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires result=pass", result.stderr)

    def test_rejects_signature_id_mismatch(self):
        ev = evidence()
        ev["signature_id"] = "other-virus"
        result = self.run_tool(ev=ev)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("signature_id does not match", result.stderr)

    def test_rejects_sample_hash_mismatch(self):
        ev = evidence()
        ev["sample_sha256"] = "b" * 64
        result = self.run_tool(ev=ev)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sample_sha256 does not match", result.stderr)


if __name__ == "__main__":
    unittest.main()
