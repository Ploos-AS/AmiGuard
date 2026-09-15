import copy
import unittest

from tools.validate_asw_handoff import validate


BASE = {
    "schema": "amiguard-asw-handoff-v1",
    "handoff_id": "fixture-001",
    "created_at": "2026-09-15T00:00:00Z",
    "producer": {"name": "ASW", "version": "0.1"},
    "sample": {
        "sha256": "a" * 64,
        "size": 1024,
        "kind": "file",
        "redistributable": False,
    },
    "analysis": {
        "result": "candidate",
        "family_hint": "fixture",
        "evidence": ["isolated static analysis fixture"],
    },
    "candidate": {
        "kind": "file",
        "offset": 16,
        "bytes": "a1b2c3d4",
        "mask": "ffffffff",
    },
}


class TestASWHandoff(unittest.TestCase):
    def test_valid_candidate(self):
        self.assertTrue(validate(copy.deepcopy(BASE)))

    def test_rejects_bad_hash(self):
        item = copy.deepcopy(BASE)
        item["sample"]["sha256"] = "bad"
        with self.assertRaises(ValueError):
            validate(item)

    def test_rejects_missing_candidate(self):
        item = copy.deepcopy(BASE)
        item["candidate"] = None
        with self.assertRaises(ValueError):
            validate(item)

    def test_rejects_kind_mismatch(self):
        item = copy.deepcopy(BASE)
        item["candidate"]["kind"] = "bootblock"
        with self.assertRaises(ValueError):
            validate(item)

    def test_clean_has_no_candidate(self):
        item = copy.deepcopy(BASE)
        item["analysis"]["result"] = "clean"
        item["candidate"] = None
        self.assertTrue(validate(item))


if __name__ == "__main__":
    unittest.main()
