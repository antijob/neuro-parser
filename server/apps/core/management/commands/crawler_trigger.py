# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from server.celery.crawler import crawl_chain


class Command(BaseCommand):
    def handle(self, *args, **options):
        crawl_chain.apply_async()
        self.stdout.write('Crawler chain triggered successfully.')
