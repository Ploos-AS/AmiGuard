import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

ROOT = os.path.dirname(os.path.dirname(__file__))
PATH = os.path.join(ROOT, "tools", "import_known_clean.py")
spec = importlib.util.spec_from_file_location("import_known_clean", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ImportKnownCleanTests(unittest.TestCase):
    def make_image(self, data):
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.write(data)
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.unlink(handle.name))
        return handle.name

    def valid_dos(self):
        block = bytearray(1024)
        block[0:4] = b"DOS\x00"
        block[4:8] = bytes.fromhex("bbb0acff")
        return bytes(block)

    def run_main(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = mod.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_candidate_clean_entry(self):
        path = self.make_image(self.valid_dos() + b"\x00" * 4096)
        rc, out, err = self.run_main([
            path, "--id", "example.clean", "--name", "Example clean",
            "--source", "local original media", "--provenance", "read from owned disk",
        ])
        self.assertEqual(rc, 0, err)
        entry = json.loads(out)
        self.assertEqual(entry["status"], "candidate-clean")
        self.assertIsNone(entry["verification"])
        self.assertEqual(entry["dos_type"], "DOS0")
        self.assertTrue(entry["checksum_valid"])
        self.assertEqual(len(entry["bootblock_sha256"]), 64)
        self.assertEqual(entry["input"]["size"], 5120)

    def test_verified_clean_status_option_is_not_exposed(self):
        path = self.make_image(self.valid_dos())
        with self.assertRaises(SystemExit) as raised:
            self.run_main([
                path, "--id", "example.clean", "--name", "Example clean",
                "--status", "verified-clean", "--source", "source",
                "--provenance", "provenance",
            ])
        self.assertEqual(raised.exception.code, 2)

    def test_verifier_option_is_not_exposed(self):
        path = self.make_image(self.valid_dos())
        with self.assertRaises(SystemExit) as raised:
            self.run_main([
                path, "--id", "example.clean", "--name", "Example clean",
                "--source", "source", "--provenance", "provenance",
                "--verifier", "independent check",
            ])
        self.assertEqual(raised.exception.code, 2)

    def test_build_entry_cannot_emit_verified_clean(self):
        path = self.make_image(self.valid_dos())
        bootblock, input_size, input_sha = mod.load_bootblock(path)

        class Args:
            entry_id = "example.clean"
            name = "Example clean"
            source = "source"
            provenance = "provenance"
            input = path

        entry = mod.build_entry(Args(), bootblock, input_size, input_sha)
        self.assertEqual(entry["status"], "candidate-clean")
        self.assertIsNone(entry["verification"])

    def test_short_input_rejected(self):
        path = self.make_image(b"short")
        rc, _, err = self.run_main([
            path, "--id", "x", "--name", "x",
            "--source", "source", "--provenance", "prov",
        ])
        self.assertEqual(rc, 2)
        self.assertIn("shorter than 1024", err)


if __name__ == "__main__":
    unittest.main()
