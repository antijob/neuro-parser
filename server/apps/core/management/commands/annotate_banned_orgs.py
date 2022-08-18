# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from server.apps.core.logic.banned_organizations import (
    annotate_banned_organizations,
)
from server.apps.core.models import MediaIncident


class Command(BaseCommand):
    def handle(self, *args, **options):
        incidents = MediaIncident.objects.filter(
            status=MediaIncident.PROCESSED_AND_ACCEPTED,
            public_title__isnull=False,
        )
        for incident in incidents:
            if not incident.public_title:
                continue
            title = annotate_banned_organizations(incident.public_title)
            if title:
                incident.public_title = title
                incident.save(update_fields=["public_title"])
