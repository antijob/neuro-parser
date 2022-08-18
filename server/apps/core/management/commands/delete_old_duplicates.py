# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.utils import timezone

from server.apps.core.models import Article, MediaIncident
from server.apps.core.logic.grabber.duplicates import (
    add_terms_to_articles,
    compare_articles_terms,
    delete_duplicated_incidents)


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_date = timezone.datetime(2020, 2, 5).date()
        end_date = timezone.now().date()
        range_in_days = range((end_date - start_date).days)
        for delta in range_in_days:
            date = start_date + timezone.timedelta(days=delta)
            articles = Article.objects.filter(
                publication_date=date,
                is_incident_created=True,
                incident__isnull=False,
                incident__status=MediaIncident.UNPROCESSED)
            if len(articles) < 2:
                continue
            articles_with_terms = add_terms_to_articles(articles)
            duplicates = compare_articles_terms(articles_with_terms)
            delete_duplicated_incidents(duplicates)
