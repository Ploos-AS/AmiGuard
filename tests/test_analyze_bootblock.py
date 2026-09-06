import importlib.util
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "tools", "analyze_bootblock.py")
SPEC = importlib.util.spec_from_file_location("analyze_bootblock", TOOL)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class AnalyzeBootblockTests(unittest.TestCase):
    def make_valid_dos(self):
        block = bytearray(1024)
        block[0:4] = b"DOS\x00"
        block[4:8] = bytes.fromhex("bbb0acff")
        return block

    def test_checksum_and_dos_type(self):
        block = self.make_valid_dos()
        self.assertTrue(MOD.checksum_valid(bytes(block)))
        self.assertEqual(MOD.dos_type(bytes(block)), "DOS0")
        block[100] = 1
        self.assertFalse(MOD.checksum_valid(bytes(block)))

    def test_extract_strings_with_offsets(self):
        block = bytearray(1024)
        block[64:72] = b"AMIGUARD"
        found = MOD.extract_strings(bytes(block), 4)
        self.assertEqual(found, [{"offset": 64, "length": 8, "text": "AMIGUARD"}])

    def test_analyze_uses_first_1024_bytes_read_only(self):
        block = self.make_valid_dos()
        block[32:40] = b"SAFEBOOT"
        image = bytes(block) + (b"X" * 2048)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sample.adf")
            with open(path, "wb") as handle:
                handle.write(image)
            before = MOD.sha256(image)
            report = MOD.analyze(path)
            with open(path, "rb") as handle:
                after_data = handle.read()
            self.assertEqual(MOD.sha256(after_data), before)
            self.assertEqual(report["input_size"], 3072)
            self.assertEqual(report["bootblock_sha256"], MOD.sha256(bytes(block)))
            self.assertEqual(report["dos_type"], "DOS0")
            self.assertTrue(any(item["text"] == "SAFEBOOT" for item in report["strings"]))

    def test_short_input_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "short.bin")
            with open(path, "wb") as handle:
                handle.write(b"x" * 100)
            with self.assertRaises(ValueError):
                MOD.analyze(path)

    def test_research_draft_cannot_be_verified(self):
        report = {
            "input_sha256": "1" * 64,
            "bootblock_sha256": "2" * 64,
        }
        draft = MOD.research_draft(report, "family.sample", "Family sample", "Family", "source")
        self.assertEqual(draft["status"], "research")
        self.assertIsNone(draft["signature"])
        self.assertEqual(draft["sample_sha256"], "2" * 64)
        self.assertEqual(draft["verifier"], "pending")


if __name__ == "__main__":
    unittest.main()
