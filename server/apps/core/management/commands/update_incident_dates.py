# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.utils import timezone

from server.apps.core.models import Article


class Command(BaseCommand):

    def handle(self, *args, **options):
        today = timezone.now().date()
        articles = Article.objects.filter(incident__isnull=False,
                                          publication_date__isnull=False,
                                          publication_date__lte=today)
        for article in articles:
            article.incident.create_date = article.publication_date
            article.incident.save()
