import json

from django.core.management.base import BaseCommand

from server.apps.core.models import DataLeak
from server.settings.components.common import BASE_DIR


class Command(BaseCommand):

    def handle(self, *args, **options):
        data_dir = BASE_DIR.joinpath(
            "server",
            "apps",
            "core",
            "management",
            "commands",
            "dc",
            "data.json"
        )

        with open(data_dir, 'r') as fp:
            data = json.load(fp)
            for item in data:
                phone = item["phone"]
                try:
                    DataLeak.objects.get(phone=phone)
                except DataLeak.DoesNotExist:
                    DataLeak.objects.create(
                        phone=phone,
                        data={"name": item["name"]}
                    )


