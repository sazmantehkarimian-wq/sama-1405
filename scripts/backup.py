import os,sqlite3,shutil,hashlib,json
from pathlib import Path
from datetime import datetime
root=Path(__file__).resolve().parents[1];data=root/'data';out=root/'backups'/datetime.now().strftime('%Y%m%d-%H%M%S');out.mkdir(parents=True)
src=data/'sama.sqlite3';dst=out/'sama.sqlite3'
with sqlite3.connect(src) as source,sqlite3.connect(dst) as target:source.backup(target)
if (data/'media').exists():shutil.copytree(data/'media',out/'media')
h=hashlib.sha256(dst.read_bytes()).hexdigest();(out/'manifest.json').write_text(json.dumps({'database_sha256':h},indent=2))
print(out)
