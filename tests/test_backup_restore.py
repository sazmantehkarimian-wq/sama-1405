import json,sqlite3
from pathlib import Path
import pytest
from django.conf import settings
from services.backup import create_backup,restore_backup,validate_backup

def make_database(path:Path,value='original'):
 db=sqlite3.connect(path)
 try:db.executescript('PRAGMA foreign_keys=ON; CREATE TABLE django_migrations(id INTEGER PRIMARY KEY); CREATE TABLE payload(id INTEGER PRIMARY KEY, value TEXT NOT NULL); INSERT INTO payload(value) VALUES (\''+value+'\');');db.commit()
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
def test_tampered_database_blocks_restore(tmp_path):
 database=tmp_path/'live.sqlite3';media=tmp_path/'media';media.mkdir();make_database(database)
 backup=create_backup(database,media,tmp_path/'backups')
 with (backup/'sama.sqlite3').open('ab') as stream:stream.write(b'tampered')
 with pytest.raises(ValueError,match='Database checksum mismatch'):validate_backup(backup)
def test_manifest_cannot_redirect_database_outside_backup(tmp_path):
 database=tmp_path/'live.sqlite3';media=tmp_path/'media';media.mkdir();make_database(database)
 backup=create_backup(database,media,tmp_path/'backups')
 manifest_path=backup/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'));manifest['database']['path']='../live.sqlite3';manifest_path.write_text(json.dumps(manifest),encoding='utf-8')
 with pytest.raises(ValueError,match='Invalid database manifest entry'):validate_backup(backup)
def test_manifest_rejects_unsafe_media_paths(tmp_path):
 database=tmp_path/'live.sqlite3';media=tmp_path/'media';media.mkdir();(media/'proof.bin').write_bytes(b'proof');make_database(database)
 backup=create_backup(database,media,tmp_path/'backups')
 manifest_path=backup/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'));manifest['media'][0]['path']='../../proof.bin';manifest_path.write_text(json.dumps(manifest),encoding='utf-8')
 with pytest.raises(ValueError,match='Unsafe media manifest path'):validate_backup(backup)
@pytest.mark.django_db
def test_maintenance_lock_rejects_writes_but_allows_reads(client):
 lock=Path(settings.DATABASES['default']['NAME']).parent/'.maintenance-lock';lock.parent.mkdir(parents=True,exist_ok=True);lock.write_text('test')
 try:
  assert client.get('/login/').status_code==200
  response=client.post('/login/',{});assert response.status_code==503
 finally:lock.unlink(missing_ok=True)