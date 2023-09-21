# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.management import call_command

from server.apps.core.logic.grabber.actions import grab_news


class Command(BaseCommand):
    def handle(self, *args, **options):
        grab_news()
