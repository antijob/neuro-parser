# -*- coding: utf-8 -*-
import json
from datetime import date

from django.core.management.base import BaseCommand

from server.apps.core.models import IncidentType, MediaIncident


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--force',
            default=False,
            action='store_true',
            help='option --force/-f to populate not empty DB'
        )

    def handle(self, *args, **options):
        with open("server/apps/core/management/commands/data/MediaIncidents.json") as fh:
            data = json.load(fh)

        if MediaIncident.objects.count() and not options.get('force'):
            raise Exception("The database isn't empty, use option --force "
                            "to populate the DB anyway")
        for item in data:
            # use first sentence of topic for public_title
            public_title = item['topic'].split('. ')[0][:512]

            incident_type = IncidentType.objects.filter(description=item['type']).first()
            incident = MediaIncident(
                public_description=item['topic'],
                public_title=public_title,
                status=MediaIncident.COMPLETED,
                region=item['region-code'],
                incident_type=incident_type,
                count=item['count'],
                urls=item['urls'],
                tags=item['tags'],
            )
            incident.save()
            incident.create_date = date.fromisoformat(item['date-iso'])
            incident.save(update_fields=['create_date'])
