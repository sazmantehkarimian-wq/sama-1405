import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from import_authorities import import_workbooks


ROOT = Path(__file__).resolve().parents[1]


class AuthorityImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.database = Path(cls.temp.name) / "uat.sqlite3"
        cls.report = Path(cls.temp.name) / "report.json"
        cls.summary = import_workbooks(ROOT, cls.database, cls.report)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_five_workbooks_and_all_sheets_are_read(self):
        self.assertEqual(self.summary["workbook_count"], 5)
        self.assertEqual(self.summary["sheet_count"], 39)

    def test_no_silent_drop_or_unmapped_field(self):
        self.assertEqual(self.summary["silent_drops"], 0)
        self.assertEqual(self.summary["field_coverage"]["unmapped"], 0)
        self.assertEqual(self.summary["field_coverage"]["percentage"], 100.0)

    def test_every_operational_or_excluded_row_is_preserved(self):
        connection = sqlite3.connect(self.database)
        raw, operational, excluded = connection.execute(
            "SELECT count(*),sum(is_operational),sum(not is_operational) FROM uat_raw_row"
        ).fetchone()
        self.assertEqual(raw, operational + excluded)
        self.assertEqual(operational, self.summary["operational_records"])

    def test_discrepancies_are_explicitly_unresolved(self):
        connection = sqlite3.connect(self.database)
        count = connection.execute(
            "SELECT count(*) FROM uat_discrepancy WHERE status='unresolved'"
        ).fetchone()[0]
        self.assertEqual(count, self.summary["unresolved_discrepancies"])

    def test_database_integrity_and_foreign_keys(self):
        connection = sqlite3.connect(self.database)
        self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_report_matches_import(self):
        self.assertEqual(json.loads(self.report.read_text(encoding="utf-8")), self.summary)


if __name__ == "__main__":
    unittest.main()
