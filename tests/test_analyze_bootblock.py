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

    def make_valid_custom(self):
        block = bytearray(1024)
        block[0:4] = bytes.fromhex("ffffffff")
        block[4:8] = bytes.fromhex("ffffffff")
        return block

    def test_checksum_and_dos_type(self):
        block = self.make_valid_dos()
        self.assertTrue(MOD.checksum_valid(bytes(block)))
        self.assertEqual(MOD.dos_type(bytes(block)), "DOS0")
        block[100] = 1
        self.assertFalse(MOD.checksum_valid(bytes(block)))

    def test_structural_classification_reason_codes(self):
        self.assertEqual(MOD.classify("DOS0", True),
                         ("STANDARD", "dos-valid-checksum"))
        self.assertEqual(MOD.classify("DOS0", False),
                         ("UNKNOWN", "dos-invalid-checksum"))
        self.assertEqual(MOD.classify(None, True),
                         ("CUSTOM", "non-dos-valid-checksum"))
        self.assertEqual(MOD.classify(None, False),
                         ("UNKNOWN", "non-dos-invalid-checksum"))

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
            self.assertEqual(report["classification"], "STANDARD")
            self.assertEqual(report["reason_code"], "dos-valid-checksum")
            self.assertFalse(report["malware_claim"])
            self.assertTrue(any(item["text"] == "SAFEBOOT" for item in report["strings"]))

    def test_valid_custom_is_neutral_custom_not_malware(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "custom.bin")
            with open(path, "wb") as handle:
                handle.write(self.make_valid_custom())
            report = MOD.analyze(path)
            self.assertEqual(report["classification"], "CUSTOM")
            self.assertEqual(report["reason_code"], "non-dos-valid-checksum")
            self.assertFalse(report["malware_claim"])

    def test_short_input_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "short.bin")
            with open(path, "wb") as handle:
                handle.write(b"x" * 100)
            with self.assertRaises(ValueError):
                MOD.analyze(path)

    def test_research_draft_does_not_claim_sample_hash(self):
        report = {
            "input_sha256": "1" * 64,
            "bootblock_sha256": "2" * 64,
        }
        draft = MOD.research_draft(report, "family.sample", "Family sample", "Family", "source")
        self.assertEqual(draft["status"], "research")
        self.assertIsNone(draft["signature"])
        self.assertIsNone(draft["sample_sha256"])
        self.assertEqual(draft["provenance"]["bootblock_sha256"], "2" * 64)
        self.assertEqual(draft["verifier"], "pending")


if __name__ == "__main__":
    unittest.main()
