# -*- coding: utf-8 -*-

"""
Celery Tasks for check pageviews rise.
"""

from django.conf import settings
from django.core.management import call_command

from server import celery_app


@celery_app.task
def check_pageviews():
    if settings.DEBUG:
        return False
    call_command("check_pageviews")
