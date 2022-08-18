# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from server.apps.core.models import MediaIncident


class Command(BaseCommand):

    def handle(self, *args, **options):
        (MediaIncident.objects
         .filter(status=MediaIncident.COMPLETED)
         .update(status=MediaIncident.PROCESSED_AND_ACCEPTED))
