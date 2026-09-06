import json
import os
import tempfile
import unittest

from tools import identify_known_bootblock as ident


class KnownCleanTests(unittest.TestCase):
    def make_fixture(self):
        block = bytearray(ident.BOOTBLOCK_SIZE)
        block[0:4] = b"DOS\x00"
        block[4:8] = bytes.fromhex("bbb0acff")
        return bytes(block)

    def test_exact_test_only_match(self):
        db = {
            "schema": 1,
            "entries": [{
                "id": "fixture",
                "name": "fixture",
                "bootblock_sha256": ident.sha256(self.make_fixture()),
                "status": "test-only",
            }],
        }
        digest, entry = ident.identify(self.make_fixture(), db)
        self.assertEqual(digest, db["entries"][0]["bootblock_sha256"])
        self.assertEqual(entry["id"], "fixture")

    def test_one_byte_change_is_unlisted(self):
        fixture = self.make_fixture()
        db = {
            "schema": 1,
            "entries": [{
                "id": "fixture",
                "name": "fixture",
                "bootblock_sha256": ident.sha256(fixture),
                "status": "test-only",
            }],
        }
        changed = bytearray(fixture)
        changed[100] = 1
        _, entry = ident.identify(bytes(changed), db)
        self.assertIsNone(entry)

    def test_verified_clean_requires_provenance(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            json.dump({
                "schema": 1,
                "entries": [{
                    "id": "bad",
                    "name": "bad",
                    "bootblock_sha256": "0" * 64,
                    "status": "verified-clean",
                }],
            }, handle)
            path = handle.name
        try:
            with self.assertRaises(ValueError):
                ident.load_database(path)
        finally:
            os.unlink(path)

    def test_duplicate_hash_rejected(self):
        digest = "1" * 64
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            json.dump({
                "schema": 1,
                "entries": [
                    {"id": "a", "name": "a", "bootblock_sha256": digest,
                     "status": "test-only"},
                    {"id": "b", "name": "b", "bootblock_sha256": digest,
                     "status": "test-only"},
                ],
            }, handle)
            path = handle.name
        try:
            with self.assertRaises(ValueError):
                ident.load_database(path)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
