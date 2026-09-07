import base64
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "promote_safe_test.py"

spec = importlib.util.spec_from_file_location("promote_safe_test", TOOL)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CANONICAL = base64.b64decode(
    "WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo="
)


class PromoteSafeTestTests(unittest.TestCase):
    def write_artifact(self, data):
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.write(data)
        handle.close()
        self.addCleanup(lambda: pathlib.Path(handle.name).unlink(missing_ok=True))
        return handle.name

    def research(self):
        return {
            "schema": 1,
            "id": "eicar-standard-av-test",
            "name": "EICAR Standard Anti-Virus Test File",
            "family": "EICAR AV-Test",
            "kind": "file",
            "status": "research",
            "synthetic": False,
            "source": {"publisher": "EICAR"},
            "provenance": {"derivation": "research"},
            "sample_sha256": None,
            "signature": None,
            "verifier": "pending",
            "cleaner": "none",
            "research": {"malware_claim": False},
        }

    def acquisition(self, data):
        return {
            "schema": 1,
            "kind": "amiguard-safe-test-acquisition",
            "id": "eicar-standard-av-test",
            "publisher": "EICAR e.V.",
            "source_url": "https://www.eicar.org/download/eicar.com.txt",
            "retrieved_at": "2026-09-07",
            "filename": "eicar.com.txt",
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "exact_standard_file": True,
            "malware_claim": False,
            "native_activation": False,
        }

    def test_builds_exact_safe_test(self):
        path = self.write_artifact(CANONICAL)
        proposal = module.build_safe_test(
            self.research(), self.acquisition(CANONICAL), path)
        self.assertEqual(proposal["status"], "safe-test")
        self.assertFalse(proposal["synthetic"])
        self.assertEqual(proposal["sample_sha256"], hashlib.sha256(CANONICAL).hexdigest())
        self.assertEqual(proposal["signature"]["offset"], 0)
        self.assertEqual(proposal["signature"]["bytes"], CANONICAL.hex())
        self.assertEqual(proposal["signature"]["mask"], "ff" * len(CANONICAL))
        self.assertEqual(proposal["safe_test"]["native_verdict"], "TEST-SIGNATURE")
        self.assertFalse(proposal["safe_test"]["malware_claim"])
        self.assertEqual(proposal["cleaner"], "none")

    def test_rejects_failed_acquisition(self):
        path = self.write_artifact(CANONICAL)
        acquisition = self.acquisition(CANONICAL)
        acquisition["exact_standard_file"] = False
        with self.assertRaises(ValueError):
            module.build_safe_test(self.research(), acquisition, path)

    def test_rejects_hash_mismatch(self):
        path = self.write_artifact(CANONICAL)
        acquisition = self.acquisition(CANONICAL)
        acquisition["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            module.build_safe_test(self.research(), acquisition, path)

    def test_rejects_native_activation_in_acquisition(self):
        path = self.write_artifact(CANONICAL)
        acquisition = self.acquisition(CANONICAL)
        acquisition["native_activation"] = True
        with self.assertRaises(ValueError):
            module.build_safe_test(self.research(), acquisition, path)


if __name__ == "__main__":
    unittest.main()
