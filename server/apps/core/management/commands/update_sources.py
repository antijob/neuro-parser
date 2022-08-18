import json

from django.core.management.base import BaseCommand

from server.apps.core.models import Source, MediaIncident


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.update_sources()
        self.update_incidents()

    def update_sources(self):
        path = 'server/apps/core/management/commands/data/sources.json'
        with open(path) as f:
            data = json.load(f)
        for url, row in data.items():
            is_active = row.get('is_active', True)
            region = row.get('region', 'RU')
            source = Source.objects.filter(url=url).first()
            if source:
                source.region = region
                source.is_active = is_active
                source.save()
            else:
                Source.objects.create(
                    url=url, is_active=is_active, region=region)

    def update_incidents(self):
        incidents = (MediaIncident.objects
                     .filter(status=MediaIncident.UNPROCESSED, region='RU')
                     .exclude(article__source__region='RU'))
        for incident in incidents:
            incident.region = incident.article.source.region
            incident.save(update_fields=['region'])
