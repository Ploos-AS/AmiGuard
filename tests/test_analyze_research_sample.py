import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "analyze_research_sample.py"


class AnalyzeResearchSampleTests(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run(["python3", str(TOOL), *map(str, args)], capture_output=True, text=True)

    def test_neutral_report(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.bin"
            p.write_bytes((0x3F3).to_bytes(4, "big") + b"HELLO-AMIGA\0" + bytes(range(32)))
            r = self.run_tool(p)
            self.assertEqual(r.returncode, 0, r.stderr)
            d = json.loads(r.stdout)
            self.assertEqual(d["kind"], "amiguard-research-sample-analysis")
            self.assertFalse(d["malware_claim"])
            self.assertFalse(d["native_activation"])
            self.assertEqual(d["interpretation"]["classification"], "UNDETERMINED")
            self.assertTrue(d["interpretation"]["requires_human_review"])
            self.assertFalse(d["interpretation"]["candidate_windows_are_signatures"])
            self.assertIsNone(d["promotion"])
            self.assertIsNone(d["cleaner"])
            self.assertIn("HUNK_HEADER", [x["record"] for x in d["observations"]["hunk_record_candidates"]])
            self.assertIn("HELLO-AMIGA", [x["text"] for x in d["observations"]["printable_strings"]])

    def test_accepts_matching_intake(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.bin"
            data = b"synthetic benign fixture"
            p.write_bytes(data)
            intake = Path(td) / "intake.json"
            intake.write_text(json.dumps({"kind": "amiguard-research-sample-intake", "id": "fixture-1", "sample": {"sha256": hashlib.sha256(data).hexdigest()}}))
            r = self.run_tool(p, "--intake", intake)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(r.stdout)["intake_id"], "fixture-1")

    def test_intake_hash_must_match(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.bin"
            p.write_bytes(b"not malware")
            intake = Path(td) / "intake.json"
            intake.write_text(json.dumps({"kind": "amiguard-research-sample-intake", "id": "x", "sample": {"sha256": "0" * 64}}))
            r = self.run_tool(p, "--intake", intake)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("does not match", r.stderr)

    def test_rejects_wrong_intake_kind(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.bin"
            p.write_bytes(b"abc")
            intake = Path(td) / "intake.json"
            intake.write_text(json.dumps({"kind": "wrong", "sample": {"sha256": hashlib.sha256(b"abc").hexdigest()}}))
            r = self.run_tool(p, "--intake", intake)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("invalid research intake kind", r.stderr)

    def test_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.bin"
            p.write_bytes(b"abc")
            link = Path(td) / "link.bin"
            link.symlink_to(p)
            self.assertNotEqual(self.run_tool(link).returncode, 0)

    def test_rejects_oversize(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.bin"
            p.write_bytes(b"A" * (128 * 1024 + 1))
            self.assertNotEqual(self.run_tool(p).returncode, 0)

    def test_writes_output_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.bin"
            out = Path(td) / "analysis.json"
            p.write_bytes(b"benign output fixture")
            r = self.run_tool(p, "-o", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout, "")
            d = json.loads(out.read_text())
            self.assertEqual(d["kind"], "amiguard-research-sample-analysis")
            self.assertFalse(d["malware_claim"])


if __name__ == "__main__":
    unittest.main()
