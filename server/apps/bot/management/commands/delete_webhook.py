# -*- coding: utf-8 -*-
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

TELEGRAM_API_BOT_URL = (
    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/deleteWebhook"
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        response = requests.get(TELEGRAM_API_BOT_URL)
        print(response.json())
