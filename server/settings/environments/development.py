# -*- coding: utf-8 -*-

"""
This file contains all the settings that defines the development server.

SECURITY WARNING: don't run with debug turned on in production!
"""

import logging

from server.settings.components.common import (
    BASE_DIR,
    INSTALLED_APPS,
    MIDDLEWARE,
)

# Setting the development status:

DEBUG = True

ALLOWED_HOSTS = [
    '*',
]

# Static files:
# https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-STATICFILES_DIRS

STATICFILES_DIRS = []

STATIC_ROOT = BASE_DIR.joinpath('public', 'static')

MEDIA_ROOT = BASE_DIR.joinpath('public', 'uploads')

# Django debug toolbar
# django-debug-toolbar.readthedocs.io

INSTALLED_APPS += (
    # 'debug_toolbar',
    'nplusone.ext.django',
)

MIDDLEWARE += (
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',

    # https://github.com/bradmontgomery/django-querycount
    # Prints how many queries were executed, useful for the APIs.
    'querycount.middleware.QueryCountMiddleware',
)


# def custom_show_toolbar(request):
#     """Only show the debug toolbar to users with the superuser flag."""
#     return request.user.is_superuser


# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK':
#         'server.settings.environments.development.custom_show_toolbar',
# }

# nplusone
# https://github.com/jmcarp/nplusone

# Should be the first in line:
MIDDLEWARE = ('nplusone.ext.django.NPlusOneMiddleware',) + MIDDLEWARE

# Raise exceptions on N+1 requests:
# NPLUSONE_RAISE = True

# Logging N+1 requests:
NPLUSONE_LOGGER = logging.getLogger('django')
NPLUSONE_LOG_LEVEL = logging.WARN
