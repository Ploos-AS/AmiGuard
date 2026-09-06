import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import triage_corpus


class TriageCorpusTests(unittest.TestCase):
    def checksum_word(self, block):
        block[4:8] = b"\x00\x00\x00\x00"
        total = 0
        for offset in range(0, 1024, 4):
            word = int.from_bytes(block[offset:offset + 4], "big")
            previous = total
            total = (total + word) & 0xffffffff
            if total < previous:
                total = (total + 1) & 0xffffffff
        value = (~total) & 0xffffffff
        block[4:8] = value.to_bytes(4, "big")

    def make_standard(self):
        block = bytearray(1024)
        block[0:4] = b"DOS\x00"
        self.checksum_word(block)
        return bytes(block)

    def make_custom(self):
        block = bytearray(1024)
        block[0:4] = b"ABCD"
        self.checksum_word(block)
        return bytes(block)

    def test_batch_counts_dedup_and_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            standard = self.make_standard()
            custom = self.make_custom()
            with open(os.path.join(directory, "a.adf"), "wb") as handle:
                handle.write(standard)
            with open(os.path.join(directory, "b.adf"), "wb") as handle:
                handle.write(standard + b"X" * 100)
            with open(os.path.join(directory, "c.bin"), "wb") as handle:
                handle.write(custom)
            with open(os.path.join(directory, "short.bin"), "wb") as handle:
                handle.write(b"short")

            report = triage_corpus.triage([directory])
            self.assertEqual(report["files_seen"], 4)
            self.assertEqual(report["files_analyzed"], 3)
            self.assertEqual(report["files_failed"], 1)
            self.assertEqual(report["unique_bootblocks"], 2)
            self.assertEqual(report["classification_counts"]["STANDARD"], 2)
            self.assertEqual(report["classification_counts"]["CUSTOM"], 1)
            self.assertEqual(report["classification_counts"]["UNKNOWN"], 0)
            self.assertEqual(len(report["duplicates"]), 1)
            self.assertEqual(report["duplicates"][0]["occurrences"], 2)
            self.assertFalse(report["malware_claim"])
            self.assertTrue(all(not item["malware_claim"] for item in report["records"]))

    def test_non_recursive_and_recursive_directory_walk(self):
        with tempfile.TemporaryDirectory() as directory:
            nested = os.path.join(directory, "nested")
            os.mkdir(nested)
            with open(os.path.join(nested, "disk.adf"), "wb") as handle:
                handle.write(self.make_standard())

            with self.assertRaisesRegex(ValueError, "no input files"):
                triage_corpus.triage([directory], recursive=False)
            report = triage_corpus.triage([directory], recursive=True)
            self.assertEqual(report["files_seen"], 1)
            self.assertEqual(report["files_analyzed"], 1)

    def test_missing_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            triage_corpus.triage(["/definitely/not/here"])


if __name__ == "__main__":
    unittest.main()
