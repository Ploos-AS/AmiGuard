import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "qualify_file_signature_candidate.py"
PATTERN = bytes.fromhex("00112233445566778899aabbccddeeff")


def review_for(data):
    return {
        "schema": 1,
        "kind": "amiguard-file-signature-candidate-review",
        "status": "research-candidate",
        "sample": {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)},
        "candidate": {"offset": 16, "length": 16, "hex": PATTERN.hex(), "mask": "ff" * 16},
        "candidate_is_verified_signature": False,
        "malware_claim": False,
        "native_activation": False,
    }


class QualifyCandidateTests(unittest.TestCase):
    def run_case(self, positive, clean_list, review=None, manifests=None):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        pp = root / "positive.bin"
        pp.write_bytes(positive)
        rp = root / "review.json"
        rp.write_text(json.dumps(review or review_for(positive)))
        cmd = ["python3", str(TOOL), str(rp), str(pp)]
        for i, data in enumerate(clean_list):
            p = root / ("clean-%d.bin" % i)
            p.write_bytes(data)
            cmd.append(str(p))
        if manifests:
            for manifest in manifests(root):
                cmd += ["--clean-manifest", str(manifest)]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_passes_positive_and_clean_regression(self):
        positive = b"P" * 16 + PATTERN + b"Q" * 16
        r = self.run_case(positive, [b"clean-one", b"X" * 64])
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertTrue(d["positive_match"])
        self.assertTrue(d["clean_regression_pass"])
        self.assertTrue(d["differential_qualification_pass"])
        self.assertFalse(d["candidate_is_verified_signature"])
        self.assertFalse(d["promotion_ready"])
        self.assertFalse(d["malware_claim"])
        self.assertFalse(d["native_activation"])

    def test_collision_fails_gate(self):
        positive = b"P" * 16 + PATTERN + b"Q" * 16
        collision = b"C" * 16 + PATTERN + b"D" * 16
        r = self.run_case(positive, [collision])
        self.assertEqual(r.returncode, 1)
        d = json.loads(r.stdout)
        self.assertFalse(d["clean_regression_pass"])
        self.assertEqual(len(d["clean_collisions"]), 1)

    def test_positive_hash_binding_fails_closed(self):
        positive = b"P" * 16 + PATTERN + b"Q" * 16
        bad = review_for(positive)
        bad["sample"]["sha256"] = "0" * 64
        r = self.run_case(positive, [b"clean"], review=bad)
        self.assertEqual(r.returncode, 2)
        self.assertIn("SHA-256 does not match", r.stderr)

    def test_manifest_is_revalidated(self):
        positive = b"P" * 16 + PATTERN + b"Q" * 16
        def manifests(root):
            clean = root / "manifest-clean.bin"
            clean.write_bytes(b"manifest clean fixture")
            manifest = root / "clean.json"
            manifest.write_text(json.dumps({
                "schema": 1,
                "kind": "amiguard-clean-file-corpus",
                "files": [{"extracted_path": str(clean), "size": clean.stat().st_size, "sha256": hashlib.sha256(clean.read_bytes()).hexdigest()}],
            }))
            return [manifest]
        r = self.run_case(positive, [], manifests=manifests)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["clean_files_tested"], 1)

    def test_non_neutral_review_rejected(self):
        positive = b"P" * 16 + PATTERN + b"Q" * 16
        bad = review_for(positive)
        bad["native_activation"] = True
        r = self.run_case(positive, [b"clean"], review=bad)
        self.assertEqual(r.returncode, 2)
        self.assertIn("neutral safety contract", r.stderr)


if __name__ == "__main__":
    unittest.main()
