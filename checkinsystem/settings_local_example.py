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

# Super admin password
SAFENUMBER = ''

# Wechatmanage.py
TOKEN = ''
APPID = ''
APPSECRET = ''

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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '',
    }
}

INTERNAL_IPS = ("127.0.0.1")