import importlib.util
import json
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "tools", "build_signature_manifest.py")
spec = importlib.util.spec_from_file_location("build_signature_manifest", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SignatureManifestTests(unittest.TestCase):
    def record(self, ident, kind="file", status="verified", synthetic=False):
        return {
            "id": ident,
            "kind": kind,
            "status": status,
            "synthetic": synthetic,
            "sample_sha256": "a" * 64 if not synthetic else None,
        }

    def test_identity_only_covers_verified_non_synthetic_records(self):
        base = [
            {"path": "signatures/files/a.json", **self.record("a")},
            {"path": "signatures/files/test.json", **self.record("test", status="safe-test")},
        ]
        first = mod.build_manifest(base)
        changed_test = list(base)
        changed_test[1] = dict(changed_test[1], id="different-test")
        second = mod.build_manifest(changed_test)
        self.assertEqual(first["database_identity"], second["database_identity"])
        self.assertEqual(first["production_signature_count"], 1)

    def test_identity_changes_when_production_set_changes(self):
        first = mod.build_manifest([
            {"path": "signatures/files/a.json", **self.record("a")}
        ])
        second = mod.build_manifest([
            {"path": "signatures/files/a.json", **self.record("a")},
            {"path": "signatures/files/b.json", **self.record("b")},
        ])
        self.assertNotEqual(first["database_identity"], second["database_identity"])

    def test_load_records_is_path_sorted_and_ignores_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "files"))
            for name, ident in (("b.json", "b"), ("a.json", "a")):
                with open(os.path.join(root, "files", name), "w", encoding="utf-8") as handle:
                    json.dump(self.record(ident), handle)
            with open(os.path.join(root, "manifest.json"), "w", encoding="utf-8") as handle:
                json.dump({"generated": True}, handle)
            records = mod.load_records(root)
            self.assertEqual([r["id"] for r in records], ["a", "b"])

    def test_empty_database_has_stable_identity(self):
        first = mod.build_manifest([])
        second = mod.build_manifest([])
        self.assertEqual(first, second)
        self.assertEqual(first["production_signature_count"], 0)


if __name__ == "__main__":
    unittest.main()
