"""
Django settings for clubbable project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import json
import os

import dj_database_url
from django.contrib.messages.constants import DEFAULT_TAGS, ERROR


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# ==============================
# Settings specific to clubbable
# ==============================

CLUB_NAME = os.environ['CLUB_NAME'].replace('_', ' ')

# Title by which to refer to members. None if not applicable
MEMBER_TITLE = os.environ.get('MEMBER_TITLE')

# Filename of club's Access database, or `None` to disable
MDB_FILENAME = os.environ.get('MDB_FILENAME')
if MDB_FILENAME:
    MDB_DUMP_URL = os.environ['MDB_DUMP_URL']
    MDB_DUMP_USERNAME = os.environ['MDB_DUMP_USERNAME']
    MDB_DUMP_PASSWORD = os.environ['MDB_DUMP_PASSWORD']

# Details for fetching files from Dropbox
DROPBOX_APP_KEY = os.environ['DROPBOX_APP_KEY']
DROPBOX_APP_SECRET = os.environ['DROPBOX_APP_SECRET']

# Mailgun settings
MAILGUN_DOMAIN = os.environ['MAILGUN_DOMAIN']
MAILGUN_API_KEY = os.environ['MAILGUN_API_KEY']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = int(os.environ['EMAIL_PORT'])
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS'].lower() in ('true', 'yes')

# Mail settings for outgoing mail
FROM_ADDRESS = os.environ['FROM_ADDRESS'].replace('_', ' ')
REPLY_TO_ADDRESS = (
    os.environ.get('REPLY_TO_ADDRESS', '').replace('_', ' ')
    or FROM_ADDRESS
)
BOUNCE_ADDRESS = (
    os.environ.get('BOUNCE_ADDRESS', '').replace('_', ' ')
    or REPLY_TO_ADDRESS
)

ADMINS = [tuple(pair) for pair in json.loads(os.environ['ADMINS'])]
EMAIL_SUBJECT_PREFIX = os.environ['EMAIL_SUBJECT_PREFIX'] + ' '
SERVER_EMAIL = os.environ['SERVER_EMAIL']

if os.environ['FILE_STORAGE_TYPE'] == 'S3':
    DEFAULT_FILE_STORAGE = 'clubbable.storage.CustomS3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_DEFAULT_ACL = None
elif os.environ['FILE_STORAGE_TYPE'] == 'SFTP':
    DEFAULT_FILE_STORAGE = 'storages.backends.sftpstorage.SFTPStorage'
    SFTP_STORAGE_HOST=os.environ['SFTP_STORAGE_HOST']
    SFTP_STORAGE_ROOT=os.environ['SFTP_STORAGE_ROOT']
    SFTP_STORAGE_PARAMS=json.loads(os.environ['SFTP_STORAGE_PARAMS'])
elif os.environ['FILE_STORAGE_TYPE'] == 'Dropbox':
    DEFAULT_FILE_STORAGE = 'storages.backends.dropbox.DropBoxStorage'
    DROPBOX_OAUTH2_TOKEN=os.environ['DROPBOX_OAUTH2_TOKEN']
    DROPBOX_ROOT_PATH=os.environ['DROPBOX_ROOT_PATH']
elif os.environ['FILE_STORAGE_TYPE'] == 'local':
    # Absolute path to the directory that will hold user-uploaded files:
    MEDIA_ROOT = os.environ['MEDIA_ROOT']
    # URL that handles the media served from MEDIA_ROOT:
    MEDIA_URL = os.environ['MEDIA_URL']

# Change the tag for error messages to "warning" so that it works nicely
# with Bootstrap classes
DEFAULT_TAGS[ERROR] = 'warning'

REDIS_URL = os.environ['REDIS_URL']
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ALWAYS_EAGER = (
    os.environ.get('CELERY_ALWAYS_EAGER', 'false').lower() in ('true', 'yes')
)


# ===============
# Django settings
# ===============

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ['DEBUG'].lower() in ('true', 'yes')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_celery_results',
    'imagekit',

    'club',
    'docs',
    'dropboxer',
    'galleries',
    'import_mdb',
    'mailer',
    'pages',
]

AUTH_USER_MODEL = 'club.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
]

ROOT_URLCONF = 'clubbable.urls'

WSGI_APPLICATION = 'clubbable.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': (
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ),
        }
    }
]

CACHES = {
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/django_cache',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en-US')
TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGIN_REDIRECT_URL = '/'

# Change the tag for error messages to "warning" so that it works nicely
# with Bootstrap classes
DEFAULT_TAGS[ERROR] = 'warning'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
if 'STATIC_URL' in os.environ:
    STATIC_URL = os.environ['STATIC_URL']
if 'STATIC_ROOT' in os.environ:
    STATIC_ROOT = os.environ['STATIC_ROOT']

REDIS_URL = os.environ['REDIS_URL']
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ALWAYS_EAGER = (
    os.environ.get('CELERY_ALWAYS_EAGER', 'false').lower() in ('true', 'yes')
)

ALLOWED_HOSTS = json.loads(os.environ['ALLOWED_HOSTS'])

if os.environ['DEPLOY_ENV'] == 'heroku':
    import django_heroku
    django_heroku.settings(locals(), allowed_hosts=False)

else:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.environ['SECRET_KEY']

    # Database
    # https://docs.djangoproject.com/en/dev/ref/settings/#databases
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }

LOGGING['loggers']['dropboxer'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
}
