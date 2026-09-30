import os,sys
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sama.settings')
import django; django.setup()
from import_pipeline.import_authorities import run
print(run(Path(sys.argv[1]).resolve()))
