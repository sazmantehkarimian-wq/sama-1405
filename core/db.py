from django.db.backends.signals import connection_created
def configure_sqlite(sender,connection,**kwargs):
 if connection.vendor=='sqlite':
  c=connection.cursor(); c.execute('PRAGMA foreign_keys=ON'); c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA busy_timeout=20000')
connection_created.connect(configure_sqlite)
