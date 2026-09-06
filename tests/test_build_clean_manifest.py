import hashlib
import json
import os
import tempfile
import unittest

from tools import build_clean_manifest


class CleanManifestTests(unittest.TestCase):
    def test_build_manifest_hashes_bootblocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = os.path.join(tmp, "a.adf")
            b = os.path.join(tmp, "b.bin")
            raw_a = b"A" * 1024 + b"tail"
            raw_b = b"B" * 1024
            with open(a, "wb") as handle:
                handle.write(raw_a)
            with open(b, "wb") as handle:
                handle.write(raw_b)

            manifest = build_clean_manifest.build([a, b])
            self.assertEqual(manifest["schema"], 1)
            self.assertEqual(manifest["kind"], "amiguard-clean-bootblock-corpus")
            self.assertEqual(len(manifest["entries"]), 2)
            self.assertEqual(
                manifest["entries"][0]["input_sha256"],
                hashlib.sha256(raw_a).hexdigest(),
            )
            self.assertEqual(
                manifest["entries"][0]["bootblock_sha256"],
                hashlib.sha256(raw_a[:1024]).hexdigest(),
            )

    def test_short_input_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "short.bin")
            with open(path, "wb") as handle:
                handle.write(b"x" * 100)
            with self.assertRaises(ValueError):
                build_clean_manifest.build([path])


if __name__ == "__main__":
    unittest.main()
