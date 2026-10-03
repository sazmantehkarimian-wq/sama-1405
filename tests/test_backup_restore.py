import json,sqlite3
from pathlib import Path
import pytest
from django.conf import settings
from services.backup import create_backup,restore_backup,validate_backup
from services.startup import StartupSafetyError, assert_schema_not_newer, startup_safety_backup

def make_database(path:Path,value='original'):
 db=sqlite3.connect(path)
 try:db.executescript('PRAGMA foreign_keys=ON; CREATE TABLE django_migrations(id INTEGER PRIMARY KEY); CREATE TABLE payload(id INTEGER PRIMARY KEY, value TEXT NOT NULL); INSERT INTO payload(value) VALUES (\''+value+'\');');db.commit()
 finally:db.close()
def make_migrated_database(path:Path,app='contenttypes',name='0001_initial'):
 db=sqlite3.connect(path)
 try:
  db.executescript('PRAGMA foreign_keys=ON; CREATE TABLE django_migrations(id INTEGER PRIMARY KEY AUTOINCREMENT, app VARCHAR(255) NOT NULL, name VARCHAR(255) NOT NULL, applied DATETIME NOT NULL); CREATE TABLE payload(id INTEGER PRIMARY KEY, value TEXT NOT NULL);')
  db.execute("INSERT INTO django_migrations(app,name,applied) VALUES(?,?,datetime('now'))",(app,name));db.execute("INSERT INTO payload(value) VALUES('live')");db.commit()
 finally:db.close()
def read_value(path):
 db=sqlite3.connect(path)
 try:return db.execute('SELECT value FROM payload').fetchone()[0]
 finally:db.close()
def test_backup_restore_covers_database_media_and_pre_restore(tmp_path):
 database=tmp_path/'live.sqlite3';media=tmp_path/'media';media.mkdir();(media/'evidence.txt').write_text('original evidence');make_database(database)
 backup=create_backup(database,media,tmp_path/'backups')
 assert validate_backup(backup)['reason']=='manual'
 db=sqlite3.connect(database)
 try:db.execute("UPDATE payload SET value='changed'");db.commit()
 finally:db.close()
 (media/'evidence.txt').write_text('changed evidence')
 pre=restore_backup(backup,database,media,tmp_path/'backups',tmp_path/'.maintenance-lock')
 assert read_value(database)=='original';assert (media/'evidence.txt').read_text()=='original evidence';assert validate_backup(pre)['reason']=='pre-restore';assert not (tmp_path/'.maintenance-lock').exists()
def test_tampered_media_blocks_restore(tmp_path):
 database=tmp_path/'live.sqlite3';media=tmp_path/'media';media.mkdir();(media/'proof.bin').write_bytes(b'proof');make_database(database)
 backup=create_backup(database,media,tmp_path/'backups');(backup/'media'/'proof.bin').write_bytes(b'tampered')
 with pytest.raises(ValueError,match='Media manifest mismatch'):validate_backup(backup)

@pytest.mark.django_db
def test_startup_rejects_database_with_unknown_newer_migration(tmp_path):
 database=tmp_path/'newer.sqlite3';make_migrated_database(database,app='properties',name='9999_future_schema')
 with pytest.raises(StartupSafetyError,match='نسخه جدیدتری'):
  assert_schema_not_newer(database)

@pytest.mark.django_db
def test_startup_safety_backup_is_verified_before_migration(tmp_path):
 database=tmp_path/'live.sqlite3';media=tmp_path/'media';media.mkdir();(media/'proof.txt').write_text('proof',encoding='utf-8');make_migrated_database(database)
 backup=startup_safety_backup(database=database,media=media,backup_root=tmp_path/'backups')
 assert backup is not None
 manifest=validate_backup(backup)
 assert manifest['reason']=='startup-safety'
 assert (backup/'media'/'proof.txt').read_text(encoding='utf-8')=='proof'

@pytest.mark.django_db
def test_maintenance_lock_rejects_writes_but_allows_reads(client):
 lock=Path(settings.DATABASES['default']['NAME']).parent/'.maintenance-lock';lock.parent.mkdir(parents=True,exist_ok=True);lock.write_text('test')
 try:
  assert client.get('/login/').status_code==200
  response=client.post('/login/',{});assert response.status_code==503
 finally:lock.unlink(missing_ok=True)
