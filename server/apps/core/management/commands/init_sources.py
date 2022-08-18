# -*- coding: utf-8 -*-

from urllib.parse import urlparse

from django.core.management.base import BaseCommand

from server.apps.core.models import Source


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("server/apps/core/management/commands/data/urls.txt") as f:
            urls = f.read().split()
        for url in urls:
            source = self.source_with_same_domain(url)
            if source:
                if source.url != url:
                    source.url = url
                    source.save()
            else:
                Source.objects.create(url=url)

    @staticmethod
    def source_with_same_domain(url):
        url_domain = urlparse(url).netloc
        sources = Source.objects.filter(url__icontains=url_domain)
        for source in sources:
            source_domain = urlparse(source.url).netloc
            if source_domain == url_domain:
                return source
