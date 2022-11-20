# -*- coding: utf-8 -*-

"""
This is a django-split-settings main file.

For more information read this:
https://github.com/sobolevn/django-split-settings

To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""

from decouple import config


from split_settings.tools import include, optional


ENV = config('DJANGO_ENV')

base_settings = [
    'components/common.py',
    'components/logging.py',
    'components/caches.py',
    'components/celery.py',
    'components/grabber.py',
    'components/sentry.py',
    "components/ckeditor.py",
    "components/telegram.py",
    "components/analytics.py",

    # You can even use glob:
    # 'components/*.py'

    # Select the right env:
    'environments/{0}.py'.format(ENV),

    # Optionally override some settings:
    optional('environments/local.py'),
]

# Include settings:
include(*base_settings)
