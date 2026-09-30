import json,sqlite3
from pathlib import Path
import pytest
from django.conf import settings
from services.backup import create_backup,restore_backup,validate_backup

def make_database(path:Path,value='original'):
 with sqlite3.connect(path) as db:
  db.executescript('PRAGMA foreign_keys=ON; CREATE TABLE django_migrations(id INTEGER PRIMARY KEY); CREATE TABLE payload(id INTEGER PRIMARY KEY, value TEXT NOT NULL); INSERT INTO payload(value) VALUES (\''+value+'\');')
def read_value(path):
 with sqlite3.connect(path) as db:return db.execute('SELECT value FROM payload').fetchone()[0]
def test_backup_restore_covers_database_media_and_pre_restore(tmp_path):
 database=tmp_path/'live.sqlite3';media=tmp_path/'media';media.mkdir();(media/'evidence.txt').write_text('original evidence');make_database(database)
 backup=create_backup(database,media,tmp_path/'backups')
 assert validate_backup(backup)['reason']=='manual'
 with sqlite3.connect(database) as db:db.execute("UPDATE payload SET value='changed'")
 (media/'evidence.txt').write_text('changed evidence')
 pre=restore_backup(backup,database,media,tmp_path/'backups',tmp_path/'.maintenance-lock')
 assert read_value(database)=='original';assert (media/'evidence.txt').read_text()=='original evidence';assert validate_backup(pre)['reason']=='pre-restore';assert not (tmp_path/'.maintenance-lock').exists()
def test_tampered_media_blocks_restore(tmp_path):
 database=tmp_path/'live.sqlite3';media=tmp_path/'media';media.mkdir();(media/'proof.bin').write_bytes(b'proof');make_database(database)
 backup=create_backup(database,media,tmp_path/'backups');(backup/'media'/'proof.bin').write_bytes(b'tampered')
 with pytest.raises(ValueError,match='Media manifest mismatch'):validate_backup(backup)
@pytest.mark.django_db
def test_maintenance_lock_rejects_writes_but_allows_reads(client):
 lock=Path(settings.DATABASES['default']['NAME']).parent/'.maintenance-lock';lock.parent.mkdir(parents=True,exist_ok=True);lock.write_text('test')
 try:
  assert client.get('/login/').status_code==200
  response=client.post('/login/',{});assert response.status_code==503
 finally:lock.unlink(missing_ok=True)
