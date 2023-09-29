# -*- coding: utf-8 -*-

"""
Celery Task for news grabber.
"""

from django.core.management import call_command

from server import celery_app
from server.apps.core.logic.grabber import duplicates
from server.apps.core.models import Article

from contextlib import contextmanager
from django.core.cache import cache

import time


LOCK_EXPIRE = 60 * 60 * 6 # 6 hours

@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        if time.monotonic() < timeout_at and status:
            cache.delete(lock_id)


@celery_app.task(bind=True)
def grab_news(self):
    with memcache_lock('grab_news_lock', self.app.oid) as acquired:
        if acquired:
            call_command('grab_news')


@celery_app.task
def process_news():
    call_command('process_news')


@celery_app.task
def search_duplicates(article_id):
    article = Article.objects.get(pk=article_id)
    history = Article.objects.filter(incident__isnull=False)
    duplicates.search_duplicates_in_history([article], history)
