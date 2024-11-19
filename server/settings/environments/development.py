"""
This file contains all the settings that defines the development server.

SECURITY WARNING: don't run with debug turned on in production!
"""

from server.settings.components.common import (
    BASE_DIR,
)

# Setting the development status:

DEBUG = True

ALLOWED_HOSTS = [
    "*",
]

# Static files:

STATICFILES_DIRS = []

STATIC_ROOT = BASE_DIR.joinpath("public", "static")

MEDIA_ROOT = BASE_DIR.joinpath("public", "uploads")
