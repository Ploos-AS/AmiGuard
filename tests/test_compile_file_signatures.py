import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "compile_file_signatures.py"

spec = importlib.util.spec_from_file_location("compile_file_signatures", TOOL)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FileSignatureCompilerTests(unittest.TestCase):
    def base_record(self):
        return {
            "schema": 1,
            "id": "example",
            "name": "Example",
            "family": "test",
            "kind": "file",
            "status": "test-only",
            "synthetic": True,
            "source": {"type": "test"},
            "provenance": {"purpose": "test"},
            "sample_sha256": None,
            "signature": {"offset": 0, "bytes": "aa", "mask": "ff"},
            "verifier": "test",
            "cleaner": "none",
        }

    def test_repository_table_is_current(self):
        result = subprocess.run(
            [sys.executable, str(TOOL), "--check"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_research_is_inactive(self):
        record = self.base_record()
        record.update({
            "status": "research",
            "synthetic": False,
            "signature": None,
        })
        module.validate("record", record)
        rendered = module.render([record])
        self.assertNotIn("Example", rendered)

    def test_qualified_is_inactive(self):
        record = self.base_record()
        record.update({
            "status": "qualified",
            "synthetic": False,
            "sample_sha256": "a" * 64,
        })
        module.validate("record", record)
        rendered = module.render([record])
        self.assertNotIn("Example", rendered)

    def test_verified_is_compiled(self):
        record = self.base_record()
        record.update({
            "status": "verified",
            "synthetic": False,
            "sample_sha256": "b" * 64,
        })
        module.validate("record", record)
        rendered = module.render([record])
        self.assertIn("Example", rendered)

    def test_signature_cannot_extend_past_file_limit(self):
        record = self.base_record()
        record["signature"]["offset"] = module.MAX_FILE_SIZE
        with self.assertRaises(ValueError):
            module.validate("record", record)

    def test_research_cannot_claim_hash(self):
        record = self.base_record()
        record.update({
            "status": "research",
            "synthetic": False,
            "sample_sha256": "c" * 64,
            "signature": None,
        })
        with self.assertRaises(ValueError):
            module.validate("record", record)


if __name__ == "__main__":
    unittest.main()
