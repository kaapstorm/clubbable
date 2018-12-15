"""
Django settings for clubbable project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# ==============================
# Settings specific to clubbable
# ==============================

CLUB_NAME = "The Pirate's Cove"

# Title by which to refer to members. None if not applicable
MEMBER_TITLE = 'Captain'

# Details for fetching files from Dropbox
DROPBOX_APP_KEY = 'app_key'
DROPBOX_APP_SECRET = 'app_secret'

# Mailgun settings
MAILGUN_DOMAIN = 'mg.example.com'
CLUB_DOMAIN = 'example.com'  # Used for mailing lists
MAILGUN_API_KEY = 'key-123456'

# Mail settings for outgoing mail
SMTP_SERVER = 'localhost'
SMTP_PORT = 0  # 0 = Default
FROM_ADDRESS = 'The Club Webmaster <webmaster@example.com>'
REPLY_TO_ADDRESS = 'The Club Secretary <secretary@example.com>'  # Optional
BOUNCE_ADDRESS = '<bounce@example.com>'  # Optional

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

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'imagekit',

    'club',
    'docs',
    'dropboxer',
    'galleries',
    'mailer',
    'website',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

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
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'club_db',
        'USER': 'club_user',
        'PASSWORD': 'club_secret',
        'HOST': '',
        'PORT': '',
    }
}

DATABASE_ROUTERS = ['import_legacy.router.LegacyDbRouter']

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = '/var/www/example.com/media/'

# URL that handles the media served from MEDIA_ROOT
MEDIA_URL = 'https://media.example.com/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_ROOT = '/var/www/example.com/static/'
STATIC_URL = 'https://static.example.com/'
