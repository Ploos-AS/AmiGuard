import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "review_file_signature_candidate.py"


def analysis(window_hex="00112233445566778899aabbccddeeff"):
    return {
        "schema": 1,
        "kind": "amiguard-research-sample-analysis",
        "sample": {"sha256": "a" * 64, "size": 64},
        "intake_id": "sample-1",
        "observations": {
            "candidate_windows": [
                {"offset": 16, "length": len(window_hex) // 2, "hex": window_hex}
            ]
        },
        "malware_claim": False,
        "native_activation": False,
    }


class ReviewFileSignatureCandidateTests(unittest.TestCase):
    def run_tool(self, report, *extra):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "analysis.json"
            p.write_text(json.dumps(report))
            return subprocess.run(
                [
                    "python3", str(TOOL), str(p),
                    "--offset", "16",
                    "--hex", "00112233445566778899aabbccddeeff",
                    "--reviewer", "fixture-reviewer",
                    "--rationale", "synthetic review fixture",
                    *extra,
                ],
                capture_output=True,
                text=True,
            )

    def test_emits_non_activating_research_candidate(self):
        r = self.run_tool(analysis())
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d["kind"], "amiguard-file-signature-candidate-review")
        self.assertEqual(d["status"], "research-candidate")
        self.assertFalse(d["candidate_is_verified_signature"])
        self.assertFalse(d["malware_claim"])
        self.assertFalse(d["native_activation"])
        self.assertIsNone(d["promotion"])
        self.assertIsNone(d["cleaner"])
        self.assertEqual(d["candidate"]["mask"], "ff" * 16)
        self.assertTrue(d["review"]["human_approved_for_further_research"])

    def test_rejects_window_not_present_in_analysis(self):
        report = analysis("ffeeddccbbaa99887766554433221100")
        r = self.run_tool(report)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("exactly match", r.stderr)

    def test_rejects_non_neutral_analysis(self):
        report = analysis()
        report["malware_claim"] = True
        r = self.run_tool(report)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("neutral safety contract", r.stderr)

    def test_rejects_bad_sha(self):
        report = analysis()
        report["sample"]["sha256"] = "bad"
        r = self.run_tool(report)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("SHA-256", r.stderr)

    def test_writes_output_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "analysis.json"
            out = Path(td) / "review.json"
            p.write_text(json.dumps(analysis()))
            r = subprocess.run(
                [
                    "python3", str(TOOL), str(p),
                    "--offset", "16",
                    "--hex", "00112233445566778899AABBCCDDEEFF",
                    "--reviewer", "fixture-reviewer",
                    "--rationale", "synthetic review fixture",
                    "-o", str(out),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout, "")
            d = json.loads(out.read_text())
            self.assertEqual(d["candidate"]["hex"], "00112233445566778899aabbccddeeff")


if __name__ == "__main__":
    unittest.main()
