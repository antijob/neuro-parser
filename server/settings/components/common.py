# -*- coding: utf-8 -*-

"""
Django settings for server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their config, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

from decouple import config as c

from server.settings.components import BASE_DIR


MODELS_DIR = BASE_DIR.joinpath('models')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
c.path = '../../../.env'
SECRET_KEY = c('DJANGO_KEY')

# Application definition:

INSTALLED_APPS = (
    # Default django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    # django-admin:
    'django.contrib.admin',
    'django.contrib.admindocs',

    # API:
    'rest_framework',
    'rest_framework.authtoken',

    # Auth:
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Tracking:
    "tracking",

    # Your apps go here:
    'server.apps.api',
    'server.apps.bot',
    'server.apps.core',
    'server.apps.users',
)

MIDDLEWARE = (
    # Content Security Policy:
    # 'csp.middleware.CSPMiddleware',

    # Django:
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'server.urls'

# WSGI_APPLICATION = 'server.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        # Choices are: postgresql, mysql, sqlite3, oracle
        "ENGINE": "django.db.backends.postgresql",
        # Database name or filepath if using 'sqlite3':
        "NAME": c('POSTGRES_DB'),
        # You don't need these settings if using 'sqlite3':
        "USER": c("POSTGRES_USER"),
        "PASSWORD": c("POSTGRES_PASSWORD"),
        "HOST": c("DB_HOST"),
        "PORT": c("DB_PORT", default=5432, cast=int),
        "CONN_MAX_AGE": c("CONN_MAX_AGE", cast=int, default=60),
    },
}

EMAIL_HOST = c("EMAIL_HOST", default="localhost")
EMAIL_HOST_USER = c("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = c("email.passwd", default="")
EMAIL_PORT = c("EMAIL_PORT", cast=int, default=25)
EMAIL_USE_TLS = c("EMAIL_USE_TLS", cast=bool, default=True)
DEFAULT_FROM_EMAIL = 'runet.report@roskomsvoboda.org'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True
USE_L10N = True

LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Russian'),
)

LOCALE_PATHS = (
    'locale/',
)

USE_TZ = True
TIME_ZONE = 'UTC'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Templates
# https://docs.djangoproject.com/en/1.11/ref/templates/api

TEMPLATES = [{
    'APP_DIRS': True,
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        # Contains plain text templates, like `robots.txt`:
        BASE_DIR.joinpath('server', 'templates'),
    ],
    'OPTIONS': {
        'context_processors': [
            # default template context processors
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.request',
        ],
    },

}]

SITE_ID = 1

AUTH_USER_MODEL = 'users.User'

# Allauth

ACCOUNT_FORMS = {
    'login': 'server.apps.users.forms.CustomLoginForm',
    'signup': 'server.apps.users.forms.CustomSignupForm',
}

LOGIN_REDIRECT_URL = 'core:dashboard'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
SOCIALACCOUNT_QUERY_EMAIL = True
USERNAME_FIELD = 'email'

# Media files
# Media-root is commonly changed in production
# (see development.py and production.py).

MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'uploads')

# Django default authentication system.
# https://docs.djangoproject.com/en/1.11/topics/auth/

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]

# REST API

API_TOKEN = c("API_TOKEN", default=None)
API_RPS = c("API_RPS", default='1/second')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'server.apps.api.authentication.EnvTokenAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': API_RPS,
    },
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ]
}

CHAT_GPT_KEY = c('CHAT_GPT_KEY')

CONTACT_FORM_EMAILS = ['agorarights@gmail.com']

MAX_UPLOAD_SIZE = 20971520
ACCOUNT_ADAPTER = 'server.apps.core.logic.account_adapter.CustomAccountAdapter'
ACCOUNT_ALLOW_SIGNUPS = False

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGIN_URL = "/s/accounts/login/"
