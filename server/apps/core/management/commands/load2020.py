# -*- coding: utf-8 -*-
import json

from django.core.management.base import BaseCommand

from server.apps.core.models import Source, Article


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('server/apps/core/management/commands/data/2020.json') as f:
            data = json.load(f)
        for (source_url, source_articles) in data:
            source = Source.objects.filter(url=source_url).first()
            if not source:
                continue
            for article_data in source_articles:
                self.add_article(article_data, source)

    @staticmethod
    def add_article(article_data, source):
        if Article.objects.filter(url=article_data['url']).exists():
            return
        return Article.objects.create(source=source,
                                      is_downloaded=True,
                                      **article_data)
