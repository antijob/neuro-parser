# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from server.celery.parser import parse_chain


class Command(BaseCommand):
    def handle(self, *args, **options):
        parse_chain.apply_async()
        self.stdout.write('Parser chain triggered successfully.')
