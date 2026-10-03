from __future__ import annotations

import sqlite3
from pathlib import Path

from django.conf import settings
from django.db import connections
from django.db.migrations.executor import MigrationExecutor

from services.backup import create_backup, verify_sqlite


class StartupSafetyError(RuntimeError):
    pass


def _database_path() -> Path:
    return Path(settings.DATABASES["default"]["NAME"])


def _applied_migrations(database: Path) -> set[tuple[str, str]]:
    if not database.exists() or database.stat().st_size == 0:
        return set()
    db = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "django_migrations" not in tables:
            return set()
        return {(row[0], row[1]) for row in db.execute("SELECT app, name FROM django_migrations")}
    finally:
        db.close()


def _known_migrations() -> set[tuple[str, str]]:
    connection = connections["default"]
    executor = MigrationExecutor(connection)
    return set(executor.loader.disk_migrations.keys())


def assert_schema_not_newer(database: Path | None = None) -> None:
    database = Path(database or _database_path())
    if not database.exists() or database.stat().st_size == 0:
        return
    verify_sqlite(database)
    applied = _applied_migrations(database)
    unknown = sorted(applied - _known_migrations())
    if unknown:
        sample = ", ".join(f"{app}.{name}" for app, name in unknown[:8])
        raise StartupSafetyError(
            "این پوشه داده با نسخه جدیدتری از سما ساخته شده است و این نسخه حق نوشتن روی آن را ندارد. "
            f"Migration ناشناخته: {sample}"
        )


def pending_migrations() -> list[tuple[str, str]]:
    connection = connections["default"]
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    return [(migration.app_label, migration.name) for migration, backwards in plan if not backwards]


def startup_safety_backup(*, database: Path | None = None, media: Path | None = None, backup_root: Path | None = None):
    database = Path(database or _database_path())
    media = Path(media or settings.MEDIA_ROOT)
    backup_root = Path(backup_root or (Path(settings.BASE_DIR) / "backups"))
    if not database.exists() or database.stat().st_size == 0:
        return None
    applied = _applied_migrations(database)
    if not applied:
        return None
    assert_schema_not_newer(database)
    return create_backup(database, media, backup_root, reason="startup-safety")


def run_preflight():
    database = _database_path()
    database.parent.mkdir(parents=True, exist_ok=True)
    Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
    assert_schema_not_newer(database)
    pending = pending_migrations() if database.exists() and database.stat().st_size else []
    backup = startup_safety_backup(database=database)
    return {"database": database, "pending": pending, "backup": backup}
