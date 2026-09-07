import json
import os
import tempfile
import unittest

from tools import preflight_safe_test as p


class SafeTestPreflightTests(unittest.TestCase):
    def write(self, data):
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.write(data)
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.unlink(handle.name))
        return handle.name

    def proposal(self, data):
        return {
            "schema": 1,
            "id": "safe-example",
            "kind": "file",
            "status": "safe-test",
            "synthetic": False,
            "sample_sha256": p.sha256(data),
            "signature": {
                "offset": 0,
                "bytes": data.hex(),
                "mask": "ff" * len(data),
            },
            "cleaner": "none",
            "safe_test": {
                "malware_claim": False,
                "native_verdict": "TEST-SIGNATURE",
            },
        }

    def write_json(self, obj):
        handle = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
        json.dump(obj, handle)
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.unlink(handle.name))
        return handle.name

    def test_passes_with_positive_and_clean_near_miss(self):
        positive_data = b"SAFE-TEST"
        proposal_path = self.write_json(self.proposal(positive_data))
        positive = self.write(positive_data)
        clean = self.write(b"SAFE-TESU")
        report = p.preflight(proposal_path, positive, [clean])
        self.assertTrue(report["positive_match"])
        self.assertTrue(report["clean_regression_pass"])
        self.assertTrue(report["preflight_pass"])
        self.assertFalse(report["malware_claim"])
        self.assertFalse(report["native_activation"])

    def test_clean_collision_fails(self):
        positive_data = b"SAFE-TEST"
        proposal_path = self.write_json(self.proposal(positive_data))
        positive = self.write(positive_data)
        clean = self.write(positive_data)
        report = p.preflight(proposal_path, positive, [clean])
        self.assertFalse(report["clean_regression_pass"])
        self.assertFalse(report["preflight_pass"])

    def test_positive_hash_mismatch_rejected(self):
        positive_data = b"SAFE-TEST"
        proposal_path = self.write_json(self.proposal(positive_data))
        wrong = self.write(b"WRONG")
        clean = self.write(b"CLEAN")
        with self.assertRaises(ValueError):
            p.preflight(proposal_path, wrong, [clean])

    def test_positive_cannot_be_in_clean_corpus(self):
        positive_data = b"SAFE-TEST"
        proposal_path = self.write_json(self.proposal(positive_data))
        positive = self.write(positive_data)
        with self.assertRaises(ValueError):
            p.preflight(proposal_path, positive, [positive])

    def test_empty_clean_corpus_never_passes(self):
        positive_data = b"SAFE-TEST"
        proposal_path = self.write_json(self.proposal(positive_data))
        positive = self.write(positive_data)
        report = p.preflight(proposal_path, positive, [])
        self.assertFalse(report["preflight_pass"])


if __name__ == "__main__":
    unittest.main()
