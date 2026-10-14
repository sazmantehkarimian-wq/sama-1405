import os,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from services.backup import create_backup
result=create_backup(Path(os.environ.get('SAMA_DB_PATH',root/'data/sama.sqlite3')),root/'data/media',Path(os.environ.get('SAMA_BACKUP_PATH',root/'backups')))
print(result)
