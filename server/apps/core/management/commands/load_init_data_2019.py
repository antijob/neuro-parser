# -*- coding: utf-8 -*-
import json
from datetime import date

from django.core.management.base import BaseCommand

from server.apps.core.models import MediaIncident


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open("server/apps/core/management/commands/data/MediaIncidents2019.json") as f:
            data = json.load(f)
        for item in data:
            if self.check_if_exists(item):
                continue

            # Create incident
            public_title = item['topic'].split('. ')[0][:512].strip()
            public_description = item['topic'].strip()
            incident_type = IncidentType.objects.filter(description=item['type']).first()
            incident = MediaIncident(
                public_description=public_description,
                public_title=public_title,
                status=MediaIncident.COMPLETED,
                region=item['region-code'],
                incident_type=incident_type,
                count=item['count'],
                urls=item['urls'],
            )
            incident.create_date = date.fromisoformat(item['date-iso'])
            incident.save()

    def check_if_exists(self, item):
        for url in item['urls']:
            url_exists = (MediaIncident.objects
                          .filter(urls__contains=item['urls'])
                          .exists())
            if url_exists:
                return True

        text_exists = (MediaIncident.objects
                       .filter(public_description=item['topic'].strip())
                       .exists())
        if text_exists:
            return True
