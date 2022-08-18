import re

from django.core.management.base import BaseCommand

from server.apps.core.models import MediaIncident

BANNED_WEBSITES = [
    'team29.org',
    'openrussia.org',
    'mbk-news.appspot.com',
    'openmedia.io',
    'amnesty.org',
]

BANNED_WEBSITES_REGEX = re.compile(r'|'.join(BANNED_WEBSITES))


class Command(BaseCommand):

    def handle(self, *args, **options):
        media_incidents = MediaIncident.objects.only('pk', 'status', 'urls', 'title', 'public_title')

        for incident in media_incidents:
            urls = incident.urls
            for url in urls:
                if BANNED_WEBSITES_REGEX.findall(url):
                    if incident.status == MediaIncident.PROCESSED_AND_ACCEPTED:
                        incident.status = MediaIncident.PROCESSED_AND_REJECTED

                    annotation = "[❌ ПЕРВОИСТОЧНИК ПРИЗНАН ЗАПРЕЩЕННЫМ В РФ]"
                    if not incident.title.startswith(annotation):
                        incident.title = f"{annotation} {incident.title}"
                        if incident.public_title:
                            incident.public_title = f"{annotation} {incident.public_title}"

                        incident.save(update_fields=['title', 'status'])

