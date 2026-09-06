import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

ROOT = os.path.dirname(os.path.dirname(__file__))
PATH = os.path.join(ROOT, "tools", "preflight_known_clean.py")
spec = importlib.util.spec_from_file_location("preflight_known_clean", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PreflightKnownCleanTests(unittest.TestCase):
    def write_json(self, value):
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8")
        json.dump(value, handle)
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.unlink(handle.name))
        return handle.name

    def candidate(self):
        return {
            "id": "example.clean",
            "name": "Example clean",
            "bootblock_sha256": "1" * 64,
            "dos_type": "DOS0",
            "checksum_valid": True,
            "status": "candidate-clean",
            "source": "documented source",
            "provenance": "preserved original media",
            "verification": None,
            "input": {"basename": "example.adf", "size": 901120, "sha256": "2" * 64},
        }

    def review(self):
        return {
            "schema": 1,
            "candidate_id": "example.clean",
            "bootblock_sha256": "1" * 64,
            "reviewer": "independent reviewer",
            "method": "independent hash and provenance review",
            "evidence": "review record reference",
            "decision": "verified-clean",
        }

    def database(self):
        return {"schema": 1, "entries": []}

    def run_main(self, candidate, review, database, extra=None):
        args = [self.write_json(candidate), self.write_json(review),
                "--database", self.write_json(database)]
        if extra:
            args.extend(extra)
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = mod.main(args)
        return rc, out.getvalue(), err.getvalue()

    def test_valid_review_passes(self):
        rc, out, err = self.run_main(self.candidate(), self.review(), self.database())
        self.assertEqual(rc, 0, err)
        self.assertIn("PREFLIGHT PASS", out)

    def test_json_output_promotes_without_mutating_candidate_file(self):
        candidate = self.candidate()
        rc, out, err = self.run_main(candidate, self.review(), self.database(), ["--json"])
        self.assertEqual(rc, 0, err)
        promoted = json.loads(out)
        self.assertEqual(promoted["status"], "verified-clean")
        self.assertEqual(promoted["verification"]["reviewer"], "independent reviewer")
        self.assertEqual(candidate["status"], "candidate-clean")

    def test_hash_mismatch_rejected(self):
        review = self.review()
        review["bootblock_sha256"] = "3" * 64
        rc, _, err = self.run_main(self.candidate(), review, self.database())
        self.assertEqual(rc, 2)
        self.assertIn("does not match candidate", err)

    def test_duplicate_hash_rejected(self):
        db = self.database()
        db["entries"].append({"id": "other", "bootblock_sha256": "1" * 64})
        rc, _, err = self.run_main(self.candidate(), self.review(), db)
        self.assertEqual(rc, 2)
        self.assertIn("already exists", err)

    def test_non_candidate_status_rejected(self):
        candidate = self.candidate()
        candidate["status"] = "verified-clean"
        rc, _, err = self.run_main(candidate, self.review(), self.database())
        self.assertEqual(rc, 2)
        self.assertIn("must be candidate-clean", err)

    def test_review_requires_evidence(self):
        review = self.review()
        review["evidence"] = ""
        rc, _, err = self.run_main(self.candidate(), review, self.database())
        self.assertEqual(rc, 2)
        self.assertIn("review requires evidence", err)


if __name__ == "__main__":
    unittest.main()
