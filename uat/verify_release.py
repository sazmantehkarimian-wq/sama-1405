#!/usr/bin/env python3
"""Programmatic release gates that are runnable on Linux CI."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import tempfile
import threading
import zipfile
from pathlib import Path


REQUIRED_TABLES = {"uat_import_batch", "uat_source_file", "uat_raw_row", "uat_field_registry", "uat_discrepancy"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def verify(package: Path) -> dict:
    report = json.loads((package / "QA/IMPORT_REPORT_4.0.0-uat.2.json").read_text(encoding="utf-8"))
    assert report["workbook_count"] == 5 and report["sheet_count"] == 39
    assert report["silent_drops"] == 0 and report["field_coverage"]["unmapped"] == 0
    launcher = (package / "START_SERVER.bat").read_text(encoding="utf-8-sig")
    firewall = (package / "FIREWALL_8765_FA.txt").read_text(encoding="utf-8")
    assert "SAMANE_AMLAK_PORT=8765" in launcher and "http://127.0.0.1:8765/" in launcher
    assert "localport=8765" in firewall and "http://SERVER-IP:8765" in firewall
    database = package / "data/database.sqlite3"
    connection = sqlite3.connect(database)
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert REQUIRED_TABLES <= tables
    operational = connection.execute("SELECT count(*) FROM uat_raw_row WHERE is_operational=1").fetchone()[0]
    discrepancy = connection.execute("SELECT count(*) FROM uat_discrepancy WHERE status='unresolved'").fetchone()[0]
    assert operational == report["operational_records"]
    assert discrepancy == report["unresolved_discrepancies"]
    connection.close()

    # Backup/restore gate.
    with tempfile.TemporaryDirectory() as temporary:
        backup = Path(temporary) / "backup.sqlite3"
        source = sqlite3.connect(database)
        target = sqlite3.connect(backup)
        source.backup(target)
        source.close(); target.close()
        restored = sqlite3.connect(backup)
        assert restored.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert restored.execute("SELECT count(*) FROM uat_raw_row").fetchone()[0] >= operational
        restored.close()

    # Five-user concurrency gate against a disposable database copy.
    with tempfile.TemporaryDirectory() as temporary:
        concurrent = Path(temporary) / "concurrent.sqlite3"
        shutil.copy2(database, concurrent)
        setup = sqlite3.connect(concurrent)
        setup.execute("CREATE TABLE uat_concurrency_test(user_id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        setup.commit(); setup.close()
        errors = []
        def writer(user_id: int):
            try:
                db = sqlite3.connect(concurrent, timeout=30)
                db.execute("PRAGMA busy_timeout=30000")
                db.execute("INSERT INTO uat_concurrency_test VALUES(?,?)", (user_id, f"user-{user_id}"))
                db.commit(); db.close()
            except Exception as exc:  # pragma: no cover - failure is reported by assertion
                errors.append(str(exc))
        threads = [threading.Thread(target=writer, args=(number,)) for number in range(1, 6)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        check = sqlite3.connect(concurrent)
        assert not errors and check.execute("SELECT count(*) FROM uat_concurrency_test").fetchone()[0] == 5
        check.close()
    return {"status": "PASS", "version": report["version"], "checks": 15,
            "operational_records": operational, "unresolved_discrepancies": discrepancy}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.package), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
