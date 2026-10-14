import os,socket
from waitress import serve
if not os.environ.get('SAMA_ALLOWED_HOSTS'):
 hosts={'127.0.0.1','localhost',socket.gethostname()}
 try:hosts.update(socket.gethostbyname_ex(socket.gethostname())[2])
 except OSError:pass
 os.environ['SAMA_ALLOWED_HOSTS']=','.join(sorted(hosts))
from sama.wsgi import application
port=int(os.environ.get('SAMA_PORT','8765'))
serve(application,host='0.0.0.0',port=port,threads=8)
