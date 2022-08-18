# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from server.apps.core.models import MediaIncident, UserIncident


class Command(BaseCommand):
    def handle(self, *args, **options):
        MediaIncident.objects.filter(incident_type=3).update(incident_type=6)
        UserIncident.objects.filter(incident_type=3).update(incident_type=6)
