# Docker Environment Settings
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'NO').lower() in ('on', 'true', 'y', 'yes')

ALLOWED_HOSTS = ['*']
DOMAIN = os.environ['DOMAIN']
CHECKINURL = os.environ['CHECKINURL']
SCHOOLEMAIL = os.environ['SCHOOLEMAIL']
QRCODEREFRESHTIME = int(os.environ['QRCODEREFRESHTIME'])  # MORE THAN 3

BROWSER_DOWNLOAD_URL = os.environ['BROWSER_DOWNLOAD_URL']  # html5 browser download url

# Wechatmanage.py
TOKEN = os.environ['WECHAT_TOKEN']
CORPID = os.environ['WECHAT_CORPID']
AGENTID = os.environ['WECHAT_AGENTID']
APPSECRET = os.environ['WECHAT_APPSECRET']
ENCODINGAESKEY = os.environ['WECHAT_ENCODINGAESKEY']
WECHATQRCODEURL = os.environ['WECHATQRCODEURL']
CONTACTSECRET = os.environ['CONTACTSECRET']
WEEK_FIRST_DAY = os.environ['WEEK_FIRST_DAY']  # 0: Sunday 1:Monday

# Database
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(conn_max_age=60),
}

if os.environ.get('ZHENGFANG_DATABASE_URL', default=None):
    DATABASES['zhengfang'] = dj_database_url.parse(os.environ['ZHENGFANG_DATABASE_URL'])

# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ['REDIS_URL'],  # example: "redis://127.0.0.1:6379/1"
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

INTERNAL_IPS = ("127.0.0.1")

# mail setting
EMAIL_HOST = os.environ['EMAIL_HOST']  # SMTP
EMAIL_PORT = os.environ['EMAIL_PORT']  # SMTP port
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']  # email address
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']  # email password
EMAIL_SUBJECT_PREFIX = os.environ['EMAIL_SUBJECT_PREFIX']  # subject-line prefix
EMAIL_USE_TLS = True
# admin email
SERVER_EMAIL = os.environ[
    'SERVER_EMAIL']  # The email address that error messages come from, such as those sent to ADMINS and MANAGERS.

# Celery
CELERY_BROKER_URL = os.environ['REDIS_URL']

CELERY_RESULT_BACKEND = os.environ['REDIS_URL']
