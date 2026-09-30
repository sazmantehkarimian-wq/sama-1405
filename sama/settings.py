from pathlib import Path
import os, secrets
BASE_DIR=Path(__file__).resolve().parent.parent
_secret_file=BASE_DIR/'data/.secret-key'
if os.environ.get('SAMA_SECRET_KEY'): SECRET_KEY=os.environ['SAMA_SECRET_KEY']
else:
 _secret_file.parent.mkdir(parents=True,exist_ok=True)
 if not _secret_file.exists(): _secret_file.write_text(secrets.token_urlsafe(64),encoding='utf-8'); _secret_file.chmod(0o600)
 SECRET_KEY=_secret_file.read_text(encoding='utf-8').strip()
DEBUG=os.environ.get('SAMA_DEBUG','0')=='1'
ALLOWED_HOSTS=[h.strip() for h in os.environ.get('SAMA_ALLOWED_HOSTS','127.0.0.1,localhost').split(',')]
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','domains.registry','domains.properties','domains.contracts','domains.operations','domains.documents','domains.identity','ui']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.locale.LocaleMiddleware','django.middleware.common.CommonMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','core.middleware.ForcePasswordChangeMiddleware','core.middleware.AuditRequestMiddleware']
ROOT_URLCONF='sama.urls'; WSGI_APPLICATION='sama.wsgi.application'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'ui/templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':Path(os.environ.get('SAMA_DB_PATH',BASE_DIR/'data/sama.sqlite3')),'OPTIONS':{'timeout':20,'transaction_mode':'IMMEDIATE'}}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':12}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'}]
LANGUAGE_CODE='fa'; TIME_ZONE='Asia/Tehran'; USE_I18N=True; USE_TZ=True
STATIC_URL='static/'; STATIC_ROOT=BASE_DIR/'collected_static'; STATICFILES_DIRS=[BASE_DIR/'design_system/static']
MEDIA_URL='media/'; MEDIA_ROOT=BASE_DIR/'data/media'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'; LOGIN_URL='login'; LOGIN_REDIRECT_URL='dashboard'; LOGOUT_REDIRECT_URL='login'
SESSION_COOKIE_HTTPONLY=True; SESSION_COOKIE_SAMESITE='Lax'; CSRF_COOKIE_SAMESITE='Lax'; SECURE_CONTENT_TYPE_NOSNIFF=True; X_FRAME_OPTIONS='DENY'
FILE_UPLOAD_MAX_MEMORY_SIZE=10*1024*1024

SECURE_SSL_REDIRECT=os.environ.get('SAMA_HTTPS','0')=='1'
SESSION_COOKIE_SECURE=SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE=SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS=31536000 if SECURE_SSL_REDIRECT else 0
