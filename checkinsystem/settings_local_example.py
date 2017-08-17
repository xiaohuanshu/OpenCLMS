# Develop Environment Settings
try:
    from settings_base import *
except:
    pass

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']
DOMAIN = 'http://DOMAIN'
CHECKINURL = 'http://DOMAIN/checkin/ck'
SCHOOLEMAIL = ''
QRCODEREFRESHTIME = 5  # MORE THAN 3
WEEK_FIRST_DAY = 1  # 0: Sunday 1:Monday

# BROWSER_DOWNLOAD_URL = "" # html5 browser download url

# Wechatmanage.py
TOKEN = ''
CORPID = ''
AGENTID = ''
APPSECRET = ''
ENCODINGAESKEY = ''
WECHATQRCODEURL = ''
CONTACTSECRET = ''

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432'
    }
}

# CACHES
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "",  # example: "redis://127.0.0.1:6379/1"
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

INTERNAL_IPS = ("127.0.0.1")

# mail setting
EMAIL_HOST = ''  # SMTP
EMAIL_PORT = 25  # SMTP port
EMAIL_HOST_USER = ''  # email address
EMAIL_HOST_PASSWORD = ''  # email password
EMAIL_SUBJECT_PREFIX = '[CheckinSystem]'  # subject-line prefix
EMAIL_USE_TLS = True
# admin email
SERVER_EMAIL = ''  # The email address that error messages come from, such as those sent to ADMINS and MANAGERS.
