import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest

from tools import qualify_eicar_acquisition as q

CANONICAL_B64 = (
    "WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo="
)


class QualifyEicarAcquisitionTests(unittest.TestCase):
    def write_temp(self, data):
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.write(data)
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.unlink(handle.name))
        return handle.name

    def test_canonical_file_passes(self):
        path = self.write_temp(base64.b64decode(CANONICAL_B64))
        report = q.qualify(path, q.EICAR_REFERENCE, "2026-09-07")
        self.assertTrue(report["exact_standard_file"])
        self.assertEqual(report["size"], 68)
        self.assertEqual(report["sha256"], q.EICAR_SHA256)
        self.assertFalse(report["malware_claim"])
        self.assertFalse(report["native_activation"])

    def test_near_miss_fails(self):
        data = bytearray(base64.b64decode(CANONICAL_B64))
        data[0] ^= 1
        path = self.write_temp(bytes(data))
        report = q.qualify(path, q.EICAR_REFERENCE, "2026-09-07")
        self.assertFalse(report["exact_standard_file"])

    def test_cli_json(self):
        path = self.write_temp(base64.b64decode(CANONICAL_B64))
        proc = subprocess.run(
            [sys.executable, "tools/qualify_eicar_acquisition.py", path,
             "--source-url", q.EICAR_REFERENCE,
             "--retrieved-at", "2026-09-07", "--json"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertTrue(report["exact_standard_file"])
        self.assertEqual(report["sha256"], q.EICAR_SHA256)


if __name__ == "__main__":
    unittest.main()
