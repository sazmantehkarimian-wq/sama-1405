import hashlib
import gzip
import tempfile
import unittest
import zipfile
from pathlib import Path

from prepare_release import LEGACY_ROOT_GLOBS, approved_logo, prepare


ROOT = Path(__file__).resolve().parents[1]


class ReleasePreparationTests(unittest.TestCase):
    def test_approved_logo_is_copied_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            for relative in ("app/_internal/staticfiles/css", "app/_internal/amlak/static/css",
                             "app/_internal/amlak/templates/amlak"):
                (package / relative).mkdir(parents=True)
            for relative in ("app/_internal/staticfiles/css/organizational_core_v340.css",
                             "app/_internal/amlak/static/css/organizational_core_v340.css"):
                (package / relative).write_text(":root{--navy-950:#041a33}", encoding="utf-8")
            prepare(ROOT, package)
            expected = approved_logo(ROOT)
            for relative in ("app/_internal/staticfiles/images/org_logo.jpeg",
                             "app/_internal/amlak/static/images/org_logo.jpeg"):
                self.assertEqual((package / relative).read_bytes(), expected)

    def test_legacy_release_metadata_is_removed(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            (package / "app/_internal/staticfiles/css").mkdir(parents=True)
            (package / "app/_internal/amlak/static/css").mkdir(parents=True)
            for name in ("VERSION_v3.8.5.txt", "RELEASE_NOTES_v3.8.5_FA.txt", "MANIFEST_SHA256_v3.8.5.txt"):
                (package / name).write_text("legacy")
            prepare(ROOT, package)
            self.assertFalse(any(package.glob("*v3*")))
            self.assertFalse((package / "CHECK_RUNNING_VERSION.bat").exists())
            self.assertIn("۴.۰.۰ UAT 3", (package / "README_FA.txt").read_text(encoding="utf-8"))

    def test_dark_navy_is_removed_from_plain_and_compressed_design_system(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            css_dir = package / "app/_internal/staticfiles/css"
            mirror = package / "app/_internal/amlak/static/css"
            css_dir.mkdir(parents=True)
            mirror.mkdir(parents=True)
            source = ":root{--navy-950:#041a33;--navy-900:#06274b}.login{background:#0b3a69}"
            for directory in (css_dir, mirror):
                path = directory / "organizational_core_v340.css"
                path.write_text(source, encoding="utf-8")
                (directory / "organizational_core_v340.css.gz").write_bytes(gzip.compress(source.encode()))
            prepare(ROOT, package)
            for directory in (css_dir, mirror):
                path = directory / "organizational_core_v340.css"
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("#041a33", text)
                self.assertNotIn("#06274b", text)
                self.assertNotIn("#0b3a69", text)
                self.assertEqual(gzip.decompress((directory / "organizational_core_v340.css.gz").read_bytes()).decode(), text)


if __name__ == "__main__":
    unittest.main()
