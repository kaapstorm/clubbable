"""
Django settings for clubbable project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.contrib.messages.constants import DEFAULT_TAGS, ERROR


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# ==============================
# Settings specific to clubbable
# ==============================

CLUB_NAME = "The Pirate's Cove"

# Title by which to refer to members. None if not applicable
MEMBER_TITLE = 'Captain'

# Support importing from legacy database
IMPORT_LEGACY = False

# Filename of club's Access database, or `None` to disable
MDB_FILENAME = 'club.mdb'

# Details for fetching files from Dropbox
DROPBOX_APP_KEY = 'app_key'
DROPBOX_APP_SECRET = 'app_secret'

# Mailgun settings
MAILGUN_DOMAIN = 'mg.example.com'
MAILGUN_API_KEY = 'key-123456'
EMAIL_HOST_USER = 'postmaster@mg.example.com'
EMAIL_HOST_PASSWORD = 'Passw0rd!'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Mail settings for outgoing mail
FROM_ADDRESS = "The Pirate's Cove <webmaster@example.com>"
REPLY_TO_ADDRESS = 'The Club Secretary <secretary@example.com>'  # Optional
BOUNCE_ADDRESS = '<bounce@example.com>'  # Optional

ADMINS = [('Admin', 'admin@example.com')]
EMAIL_SUBJECT_PREFIX = '[clubbable] '
SERVER_EMAIL = 'clubbable@example.com'

# ===============
# Django settings
# ===============

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'change_me'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


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
]
if IMPORT_LEGACY:
    INSTALLED_APPS.append('import_legacy')

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

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'clubbable', 'db', 'db.sqlite3'),
    }
}
if IMPORT_LEGACY:
    DATABASES['legacy'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'club_db',
        'USER': 'club_user',
        'PASSWORD': 'club_secret',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
    DATABASE_ROUTERS = ['import_legacy.router.LegacyDbRouter']

CACHES = {
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/django_cache',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_REDIRECT_URL = '/'

# Change the tag for error messages to "warning" so that it works nicely
# with Bootstrap classes
DEFAULT_TAGS[ERROR] = 'warning'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = '/var/www/example.com/media/'

# URL that handles the media served from MEDIA_ROOT
MEDIA_URL = 'https://media.example.com/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'clubbable', 'static')
STATIC_URL = 'https://static.example.com/'

CELERY_RESULT_BACKEND = 'django-cache'
CELERY_BROKER_URL = 'amqp://guest:guest@rabbit:5672//'
