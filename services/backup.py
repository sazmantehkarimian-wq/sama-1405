"""Verified database/media backup and offline restore primitives."""
from __future__ import annotations
import hashlib,json,os,shutil,sqlite3,tempfile
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path
MANIFEST_VERSION=1
def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def verify_sqlite(path:Path)->None:
 with sqlite3.connect(f'file:{path}?mode=ro',uri=True) as db:
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity check failed')
  if db.execute('PRAGMA foreign_key_check').fetchone() is not None:raise ValueError('SQLite foreign-key check failed')
  tables={row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
  if 'django_migrations' not in tables:raise ValueError('Backup is not a migrated SAMA database')
def _media_entries(root:Path)->list[dict]:
 if not root.exists():return []
 return [{'path':p.relative_to(root).as_posix(),'size':p.stat().st_size,'sha256':sha256(p)} for p in sorted(root.rglob('*')) if p.is_file()]
def create_backup(database:Path,media:Path,destination_root:Path,reason='manual')->Path:
 database=Path(database);media=Path(media);destination_root=Path(destination_root);destination_root.mkdir(parents=True,exist_ok=True)
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=destination_root/f'sama-backup-{stamp}';out.mkdir()
 target=out/'sama.sqlite3'
 with sqlite3.connect(database) as source,sqlite3.connect(target) as destination:source.backup(destination)
 verify_sqlite(target)
 if media.exists():shutil.copytree(media,out/'media')
 manifest={'format':MANIFEST_VERSION,'created_at':datetime.now(timezone.utc).isoformat(),'reason':reason,'database':{'path':'sama.sqlite3','size':target.stat().st_size,'sha256':sha256(target)},'media':_media_entries(out/'media')}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2),encoding='utf-8')
 return out
def validate_backup(backup:Path)->dict:
 backup=Path(backup);manifest=json.loads((backup/'manifest.json').read_text(encoding='utf-8'))
 if manifest.get('format')!=MANIFEST_VERSION:raise ValueError('Unsupported backup format')
 database=backup/manifest['database']['path']
 if database.stat().st_size!=manifest['database']['size'] or sha256(database)!=manifest['database']['sha256']:raise ValueError('Database checksum mismatch')
 verify_sqlite(database)
 actual=_media_entries(backup/'media')
 if actual!=manifest.get('media',[]):raise ValueError('Media manifest mismatch')
 return manifest
@contextmanager
def write_lock(lock_file:Path):
 lock_file=Path(lock_file);lock_file.parent.mkdir(parents=True,exist_ok=True)
 descriptor=os.open(lock_file,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 try:
  os.write(descriptor,str(os.getpid()).encode());os.close(descriptor);yield
 finally:lock_file.unlink(missing_ok=True)
def restore_backup(backup:Path,database:Path,media:Path,backup_root:Path,lock_file:Path)->Path:
 backup=Path(backup);database=Path(database);media=Path(media)
 validate_backup(backup)
 with write_lock(lock_file):
  pre_restore=create_backup(database,media,backup_root,reason='pre-restore')
  staging=Path(tempfile.mkdtemp(prefix='.restore-',dir=database.parent))
  try:
   staged_db=staging/'sama.sqlite3';shutil.copy2(backup/'sama.sqlite3',staged_db);verify_sqlite(staged_db)
   staged_media=staging/'media'
   if (backup/'media').exists():shutil.copytree(backup/'media',staged_media)
   old_db=database.with_suffix(database.suffix+'.before-restore');database.replace(old_db);staged_db.replace(database)
   old_media=media.with_name(media.name+'.before-restore')
   if media.exists():media.replace(old_media)
   if staged_media.exists():staged_media.replace(media)
   else:media.mkdir(parents=True,exist_ok=True)
   verify_sqlite(database);validate_backup(backup)
   old_db.unlink(missing_ok=True);shutil.rmtree(old_media,ignore_errors=True)
  except Exception:
   if old_db.exists(): database.unlink(missing_ok=True);old_db.replace(database)
   if 'old_media' in locals() and old_media.exists():shutil.rmtree(media,ignore_errors=True);old_media.replace(media)
   raise
  finally:shutil.rmtree(staging,ignore_errors=True)
 return pre_restore
