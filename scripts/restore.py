import os,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from services.backup import restore_backup
if len(sys.argv)!=2:raise SystemExit('usage: python scripts/restore.py BACKUP_DIRECTORY')
database=Path(os.environ.get('SAMA_DB_PATH',root/'data/sama.sqlite3'))
pre=restore_backup(Path(sys.argv[1]),database,root/'data/media',Path(os.environ.get('SAMA_BACKUP_PATH',root/'backups')),root/'data/.maintenance-lock')
print(f'restore verified; pre-restore backup: {pre}')
