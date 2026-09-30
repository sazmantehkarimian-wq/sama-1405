import hashlib,json,shutil,sqlite3,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];backup=Path(sys.argv[1]);manifest=json.loads((backup/'manifest.json').read_text());db=backup/'sama.sqlite3'
if hashlib.sha256(db.read_bytes()).hexdigest()!=manifest['database_sha256']:raise SystemExit('invalid backup hash')
with sqlite3.connect(db) as c:
 if c.execute('pragma integrity_check').fetchone()[0]!='ok':raise SystemExit('invalid sqlite backup')
exec(open(root/'scripts/backup.py').read());shutil.copy2(db,root/'data/sama.sqlite3')
if (backup/'media').exists():shutil.copytree(backup/'media',root/'data/media',dirs_exist_ok=True)
