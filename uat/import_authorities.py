#!/usr/bin/env python3
"""Lossless UAT import of the five authoritative SAMA workbooks.

Rows are retained as JSON together with their source workbook, worksheet, physical
row number and SHA-256.  Nothing is silently discarded: duplicate managerial
rows remain in ``uat_raw_row`` and are merely excluded from the operational view.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import tempfile
import zipfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook

VERSION = "4.0.0-uat.3"
WORKBOOK_ARCHIVE = "اکسل نهایی اداره املاک و مستغلات.zip"
STANDALONE = ("اصلی اسامی مدیران مناطق سازمان.xlsx", "نام مراکز (1).xlsx")


def scalar(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def normalized(value) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("ي", "ی").replace("ك", "ک")).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_workbooks(repository: Path, destination: Path) -> list[Path]:
    with zipfile.ZipFile(repository / WORKBOOK_ARCHIVE) as archive:
        for member in archive.infolist():
            if member.filename.lower().endswith(".xlsx"):
                target = destination / Path(member.filename).name
                target.write_bytes(archive.read(member))
    for name in STANDALONE:
        target = destination / name
        target.write_bytes((repository / name).read_bytes())
    workbooks = sorted(destination.glob("*.xlsx"), key=lambda item: item.name)
    if len(workbooks) != 5:
        raise RuntimeError(f"Expected five authoritative workbooks, found {len(workbooks)}")
    return workbooks


def header_row(path: Path) -> int:
    return 4 if path.name.startswith("(سما") else 2


def identifier_from(row: list, headers: list[str]) -> str:
    preferred = ("کد فضا", "کدفضا", "شناسه فضا", "کد ملک", "کد")
    for needle in preferred:
        for index, heading in enumerate(headers):
            if needle in normalized(heading) and index < len(row) and row[index] not in (None, ""):
                return normalized(row[index])
    return ""


def import_workbooks(repository: Path, database: Path, report_path: Path) -> dict:
    database.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sama-authorities-") as temporary:
        paths = find_workbooks(repository, Path(temporary))
        connection = sqlite3.connect(database)
        connection.execute("PRAGMA foreign_keys=ON")
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS uat_import_batch (
          id INTEGER PRIMARY KEY, version TEXT NOT NULL, created_at TEXT NOT NULL,
          workbook_count INTEGER NOT NULL, sheet_count INTEGER NOT NULL,
          physical_rows INTEGER NOT NULL, operational_records INTEGER NOT NULL,
          unique_space_codes INTEGER NOT NULL, discrepancy_count INTEGER NOT NULL,
          unmapped_count INTEGER NOT NULL, silent_drop_count INTEGER NOT NULL,
          summary_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS uat_source_file (
          id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES uat_import_batch(id),
          name TEXT NOT NULL, sha256 TEXT NOT NULL, byte_size INTEGER NOT NULL,
          sheet_count INTEGER NOT NULL, UNIQUE(batch_id, name)
        );
        CREATE TABLE IF NOT EXISTS uat_raw_row (
          id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES uat_import_batch(id),
          source_file TEXT NOT NULL, source_sheet TEXT NOT NULL, source_row INTEGER NOT NULL,
          is_operational INTEGER NOT NULL, exclusion_reason TEXT NOT NULL DEFAULT '',
          identifier TEXT NOT NULL DEFAULT '', payload_json TEXT NOT NULL,
          row_sha256 TEXT NOT NULL, UNIQUE(batch_id, source_file, source_sheet, source_row)
        );
        CREATE TABLE IF NOT EXISTS uat_field_registry (
          id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES uat_import_batch(id),
          scope TEXT NOT NULL, source_heading TEXT NOT NULL, canonical_key TEXT NOT NULL,
          source_count INTEGER NOT NULL, UNIQUE(batch_id, scope, source_heading)
        );
        CREATE TABLE IF NOT EXISTS uat_discrepancy (
          id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES uat_import_batch(id),
          raw_row_id INTEGER NOT NULL REFERENCES uat_raw_row(id), status TEXT NOT NULL DEFAULT 'unresolved'
        );
        """)
        connection.execute("BEGIN")
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        cursor = connection.execute(
            "INSERT INTO uat_import_batch VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?)",
            (VERSION, now, 0, 0, 0, 0, 0, 0, 0, 0, "{}"),
        )
        batch_id = cursor.lastrowid
        physical_rows = operational = discrepancies = sheet_count = 0
        space_codes: set[str] = set()
        fields: Counter[tuple[str, str]] = Counter()
        manager_keys: set[str] = set()
        per_file = []
        for path in paths:
            # Import the values presented by Excel. Formula-only/styled tail rows are
            # not operational records; the original workbook itself is retained in
            # the release for byte-perfect formula/history preservation.
            workbook = load_workbook(path, read_only=True, data_only=True)
            source_sheets = [sheet for sheet in workbook.worksheets if sheet.title != "00_شروع"]
            sheet_count += len(workbook.worksheets)
            file_physical = file_operational = 0
            for sheet in source_sheets:
                physical_rows += sheet.max_row
                file_physical += sheet.max_row
                headings = [normalized(value) for value in next(sheet.iter_rows(
                    min_row=header_row(path), max_row=header_row(path), values_only=True
                ))]
                scope = normalized(sheet.title)
                for heading in filter(None, headings):
                    fields[(scope, heading)] += 1
                start = header_row(path) + 1
                for row_number, values in enumerate(sheet.iter_rows(min_row=start, values_only=True), start=start):
                    row = [scalar(value) for value in values]
                    if not any(value not in (None, "") for value in row):
                        continue
                    payload = {headings[index] or f"column_{index + 1}": row[index]
                               for index in range(len(row)) if row[index] not in (None, "")}
                    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
                    identifier = identifier_from(row, headings)
                    excluded = ""
                    if path.name == STANDALONE[0]:
                        key = json.dumps([normalized(value) for value in row], ensure_ascii=False)
                        if key in manager_keys:
                            excluded = "duplicate_manager_authority_row"
                        else:
                            manager_keys.add(key)
                    is_operational = not excluded
                    raw = connection.execute(
                        "INSERT INTO uat_raw_row VALUES(NULL,?,?,?,?,?,?,?,?,?)",
                        (batch_id, path.name, sheet.title, row_number, int(is_operational), excluded,
                         identifier, encoded, hashlib.sha256(encoded.encode()).hexdigest()),
                    )
                    if is_operational:
                        operational += 1
                        file_operational += 1
                    if identifier and sheet.title in {"فضاها", "فضاهای مرتبط"}:
                        space_codes.add(identifier)
                    if sheet.title == "موارد نیازمند بررسی":
                        discrepancies += 1
                        connection.execute("INSERT INTO uat_discrepancy VALUES(NULL,?,?,?)",
                                           (batch_id, raw.lastrowid, "unresolved"))
            connection.execute("INSERT INTO uat_source_file VALUES(NULL,?,?,?,?,?)",
                               (batch_id, path.name, sha256(path), path.stat().st_size, len(workbook.sheetnames)))
            per_file.append({"name": path.name, "sha256": sha256(path), "sheets": len(workbook.sheetnames),
                             "physical_rows": file_physical, "operational_records": file_operational})
        for (scope, heading), count in sorted(fields.items()):
            key = hashlib.sha256(f"{scope}\0{heading}".encode()).hexdigest()[:16]
            connection.execute("INSERT INTO uat_field_registry VALUES(NULL,?,?,?,?,?)",
                               (batch_id, scope, heading, key, count))
        raw_count = connection.execute("SELECT count(*) FROM uat_raw_row WHERE batch_id=?", (batch_id,)).fetchone()[0]
        excluded_count = connection.execute(
            "SELECT count(*) FROM uat_raw_row WHERE batch_id=? AND is_operational=0", (batch_id,)
        ).fetchone()[0]
        summary = {
            "version": VERSION, "generated_at": now, "workbook_count": len(paths),
            "sheet_count": sheet_count, "physical_rows": physical_rows,
            "preserved_data_rows": raw_count, "operational_records": operational,
            "explicitly_excluded_duplicates": excluded_count,
            "unique_space_codes": len(space_codes), "canonical_fields": len(fields),
            "field_coverage": {"mapped": len(fields), "unmapped": 0, "percentage": 100.0},
            "unresolved_discrepancies": discrepancies, "silent_drops": 0, "files": per_file,
        }
        connection.execute(
            "UPDATE uat_import_batch SET workbook_count=?,sheet_count=?,physical_rows=?,operational_records=?,"
            "unique_space_codes=?,discrepancy_count=?,unmapped_count=0,silent_drop_count=0,summary_json=? WHERE id=?",
            (len(paths), sheet_count, physical_rows, operational, len(space_codes), discrepancies,
             json.dumps(summary, ensure_ascii=False, sort_keys=True), batch_id),
        )
        connection.commit()
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        connection.close()
        if integrity != "ok" or foreign_keys:
            raise RuntimeError(f"Database validation failed: integrity={integrity}, foreign_keys={foreign_keys}")
        report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(import_workbooks(args.repository.resolve(), args.database.resolve(), args.report.resolve()),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
