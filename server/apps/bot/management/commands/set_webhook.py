# -*- coding: utf-8 -*-
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

TELEGRAM_API_BOT_URL = (
    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        response = requests.get(
            TELEGRAM_API_BOT_URL,
            params={
                "url": "https://runet.report/bot/",
                "drop_pending_updates": True,
            },
        )

        print(response.json())
