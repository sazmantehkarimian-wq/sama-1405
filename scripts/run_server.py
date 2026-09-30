import os
from waitress import serve
from sama.wsgi import application
port=int(os.environ.get('SAMA_PORT','8765'))
serve(application,host='0.0.0.0',port=port,threads=8)
