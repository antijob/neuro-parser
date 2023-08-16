# -*- coding: utf-8 -*-

import re

import requests
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

from server.apps.core.logic.grabber.actions import (
    apply_tags,
    create_incidents,
    delete_duplicates,
    rate_articles,
)
from server.apps.core.logic.grabber.article_parser import random_headers
from server.apps.core.logic.grabber.source_parser import grab_archive
from server.apps.core.models import Source

START_DATE = timezone.datetime(2021, 1, 1).date()
FIRST_PAGE_URL_TEMPLATE = (
    "https://epp.genproc.gov.ru/web/proc_{region_code}/mass-media/news/archive"
    "?p_p_id=ru_voskhod_gpparf_portal_feeds_main_page_portlet"
    "_FeedsListViewPortlet_INSTANCE_{portlet_id}"
    "&p_p_lifecycle=0&p_p_state=normal"
    "&p_p_mode=view&_ru_voskhod_gpparf_portal_feeds_main_page_portlet"
    "_FeedsListViewPortlet_INSTANCE_{portlet_id}_filterSet=true"
    "&_ru_voskhod_gpparf_portal_feeds_main_page_portlet"
    "_FeedsListViewPortlet_INSTANCE_{portlet_id}_delta=40"
    "&_ru_voskhod_gpparf_portal_feeds_main_page_portlet"
    "_FeedsListViewPortlet_INSTANCE_{portlet_id}_resetCur=false"
    "&_ru_voskhod_gpparf_portal_feeds_main_page_portlet_"
    "FeedsListViewPortlet_INSTANCE_{portlet_id}_cur=1"
)


class Command(BaseCommand):
    def get_archive_url(self, source_url):
        headers = random_headers()
        response = requests.get("%sarchive/" % source_url, headers=headers)
        if not response.status_code == 200:
            return

        match = re.search(r"_INSTANCE_([A-Za-z0-9]+)_", response.text)
        portlet_id = match.group(1)
        match = re.search(r"\/proc_(\d{2})\/", source_url)
        region_code = match.group(1)
        return FIRST_PAGE_URL_TEMPLATE.format(
            region_code=region_code, portlet_id=portlet_id
        )

    def handle(self, *args, **options):
        sources = (
            Source.objects.filter(
                is_active=True, url__contains="epp.genproc.gov.ru"
            )
            .annotate(
                article_count=Count(
                    "id", filter=Q(articles__publication_date__gte=START_DATE)
                )
            )
            .filter(article_count=0)
        )

        for source in sources:
            archive_url = self.get_archive_url(source.url)
            if archive_url:
                grab_archive(
                    source, first_page_url=archive_url, start_date=START_DATE
                )
        create_incidents()
        apply_tags()
        delete_duplicates()
