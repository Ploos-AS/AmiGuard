import os
import tempfile
import unittest

from tools import intake_research_sample as i


class ResearchSampleIntakeTests(unittest.TestCase):
    def write(self, data):
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.write(data)
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.unlink(handle.name))
        return handle.name

    def test_intake_records_hash_without_embedding_bytes(self):
        path = self.write(b"research-artifact")
        report = i.intake(path, "operator", "local test fixture", label="candidate")
        self.assertEqual(report["status"], "research")
        self.assertEqual(report["sha256"], i.sha256_file(path))
        self.assertEqual(report["size"], len(b"research-artifact"))
        self.assertFalse(report["sample_bytes_embedded"])
        self.assertFalse(report["malware_claim"])
        self.assertFalse(report["native_activation"])
        self.assertEqual(report["cleaner"], "none")
        self.assertNotIn(os.path.dirname(path), str(report))

    def test_expected_hash_passes(self):
        path = self.write(b"candidate")
        report = i.intake(
            path,
            "archive",
            "operator supplied",
            expected_sha256=i.sha256_file(path).upper(),
        )
        self.assertTrue(report["read_only_integrity_pass"])

    def test_expected_hash_mismatch_rejected(self):
        path = self.write(b"candidate")
        with self.assertRaises(ValueError):
            i.intake(path, "archive", "operator supplied", expected_sha256="0" * 64)

    def test_invalid_expected_hash_rejected(self):
        path = self.write(b"candidate")
        with self.assertRaises(ValueError):
            i.intake(path, "archive", "operator supplied", expected_sha256="xyz")

    def test_empty_source_or_provenance_rejected(self):
        path = self.write(b"candidate")
        with self.assertRaises(ValueError):
            i.intake(path, "", "provenance")
        with self.assertRaises(ValueError):
            i.intake(path, "source", "")

    def test_symlink_rejected(self):
        target = self.write(b"candidate")
        link = target + ".link"
        os.symlink(target, link)
        self.addCleanup(lambda: os.path.lexists(link) and os.unlink(link))
        with self.assertRaises(ValueError):
            i.intake(link, "source", "provenance")


if __name__ == "__main__":
    unittest.main()
