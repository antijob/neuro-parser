# -*- coding: utf-8 -*-

"""
Celery Task for news grabber.
"""

from django.core.management import call_command

from server import celery_app
from server.apps.core.logic.grabber import duplicates
from server.apps.core.models import Article


@celery_app.task
def grab_news():
    call_command('grab_news')


@celery_app.task
def process_news():
    call_command('process_news')


@celery_app.task
def search_duplicates(article_id):
    article = Article.objects.get(pk=article_id)
    history = Article.objects.filter(incident__isnull=False)
    duplicates.search_duplicates_in_history([article], history)
