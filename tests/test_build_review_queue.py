import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "tools", "build_review_queue.py")
SPEC = importlib.util.spec_from_file_location("build_review_queue", TOOL)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ReviewQueueTests(unittest.TestCase):
    def report(self):
        return {
            "schema": 1,
            "kind": "amiguard-bootblock-corpus-triage",
            "records": [
                {"path": "/a", "bootblock_sha256": "a" * 64,
                 "classification": "STANDARD", "reason_code": "dos-valid-checksum", "strings": []},
                {"path": "/b", "bootblock_sha256": "b" * 64,
                 "classification": "UNKNOWN", "reason_code": "dos-invalid-checksum",
                 "strings": [{"text": "ODD"}]},
                {"path": "/c", "bootblock_sha256": "c" * 64,
                 "classification": "CUSTOM", "reason_code": "non-dos-valid-checksum",
                 "strings": [{"text": "BOOT"}]},
                {"path": "/d", "bootblock_sha256": "c" * 64,
                 "classification": "CUSTOM", "reason_code": "non-dos-valid-checksum",
                 "strings": [{"text": "BOOT"}, {"text": "MENU"}]},
            ],
        }

    def test_standard_is_excluded_and_unique_nonstandard_is_queued(self):
        queue = MOD.build_queue(self.report())
        self.assertEqual(queue["item_count"], 2)
        self.assertEqual([item["classification"] for item in queue["items"]],
                         ["CUSTOM", "UNKNOWN"])
        self.assertFalse(queue["malware_claim"])

    def test_duplicates_are_collapsed(self):
        queue = MOD.build_queue(self.report())
        custom = queue["items"][0]
        self.assertEqual(custom["occurrences"], 2)
        self.assertEqual(custom["paths"], ["/c", "/d"])
        self.assertEqual(custom["strings"], ["BOOT", "MENU"])
        self.assertFalse(custom["malware_claim"])

    def test_inconsistent_duplicate_is_rejected(self):
        report = self.report()
        report["records"][3]["classification"] = "UNKNOWN"
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            MOD.build_queue(report)

    def test_invalid_report_rejected(self):
        with self.assertRaises(ValueError):
            MOD.build_queue({"schema": 2, "kind": "bad", "records": []})


if __name__ == "__main__":
    unittest.main()
