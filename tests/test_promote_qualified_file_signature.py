import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "promote_qualified_file_signature.py"


def review():
    return {
        "schema": 1,
        "kind": "amiguard-file-signature-candidate-review",
        "status": "research-candidate",
        "sample": {"sha256": "a" * 64, "size": 64},
        "candidate": {
            "offset": 8,
            "length": 16,
            "hex": "00112233445566778899aabbccddeeff",
            "mask": "ff" * 16,
        },
        "review": {
            "reviewer": "fixture-reviewer",
            "rationale": "synthetic candidate worth further research",
            "human_approved_for_further_research": True,
        },
        "candidate_is_verified_signature": False,
        "malware_claim": False,
        "native_activation": False,
    }


def qualification():
    return {
        "schema": 1,
        "kind": "amiguard-file-signature-candidate-qualification",
        "candidate_status": "research-candidate",
        "sample_sha256": "a" * 64,
        "sample_size": 64,
        "positive_match": True,
        "clean_files_tested": 963,
        "clean_collisions": [],
        "clean_regression_pass": True,
        "differential_qualification_pass": True,
        "candidate_is_verified_signature": False,
        "promotion_ready": False,
        "malware_claim": False,
        "native_activation": False,
    }


class PromoteQualifiedFileSignatureTests(unittest.TestCase):
    def run_tool(self, r=None, q=None):
        with tempfile.TemporaryDirectory() as td:
            rp = Path(td) / "review.json"
            qp = Path(td) / "qualification.json"
            rp.write_text(json.dumps(r or review()))
            qp.write_text(json.dumps(q or qualification()))
            return subprocess.run([
                "python3", str(TOOL), str(rp), str(qp),
                "--id", "fixture-virus",
                "--name", "Fixture Virus",
                "--family", "Fixture",
                "--source", "synthetic fixture source",
                "--provenance", "synthetic fixture provenance",
                "--verifier", "manual-sample-backed-verifier",
            ], capture_output=True, text=True)

    def test_emits_compiler_compatible_qualified_proposal(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["kind"], "file")
        self.assertEqual(data["status"], "qualified")
        self.assertFalse(data["synthetic"])
        self.assertEqual(data["sample_sha256"], "a" * 64)
        self.assertEqual(data["signature"]["offset"], 8)
        self.assertFalse(data["candidate_is_verified_signature"])
        self.assertFalse(data["malware_claim"])
        self.assertFalse(data["native_activation"])
        self.assertTrue(data["requires_visible_native_runtime"])
        self.assertEqual(data["cleaner"], "none")

    def test_rejects_failed_qualification(self):
        q = qualification()
        q["differential_qualification_pass"] = False
        result = self.run_tool(q=q)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("did not pass", result.stderr)

    def test_rejects_sample_mismatch(self):
        q = qualification()
        q["sample_sha256"] = "b" * 64
        result = self.run_tool(q=q)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match review", result.stderr)

    def test_rejects_collisions(self):
        q = qualification()
        q["clean_collisions"] = [{"sha256": "c" * 64}]
        result = self.run_tool(q=q)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("collisions", result.stderr)

    def test_rejects_non_neutral_review(self):
        r = review()
        r["native_activation"] = True
        result = self.run_tool(r=r)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("neutral safety contract", result.stderr)


if __name__ == "__main__":
    unittest.main()
