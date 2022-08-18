# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.utils import timezone
from tracking.models import Pageview

from server.records.logic import notifier

MESSAGE = (
    "* Количество просмотров выросло на {rise}% на последний час ({views} просмотров) *"
)
INTERVAL_IN_MINUTES = 60
MIN_VIEWS_PER_INTERVAL = 100
MIN_RISE_IN_PERCENTS = 100


class Command(BaseCommand):
    """
    Check pageviews for fast rises
    """

    def handle(self, *args, **options):
        now = timezone.now()
        interval_ago = now - timezone.timedelta(minutes=INTERVAL_IN_MINUTES)
        double_interval_ago = interval_ago - timezone.timedelta(
            minutes=INTERVAL_IN_MINUTES
        )

        # Count views per two last intervals
        views_per_interval = Pageview.objects.filter(
            view_time__range=(interval_ago, now)
        ).count()
        if views_per_interval < MIN_VIEWS_PER_INTERVAL:
            return
        views_per_previous_interval = Pageview.objects.filter(
            view_time__range=(double_interval_ago, interval_ago)
        ).count()
        if not views_per_previous_interval:
            return  # to prevent zero division at next line

        # Check difference between intervals
        diff = views_per_interval - views_per_previous_interval
        rise = diff / views_per_interval * 100
        if rise <= MIN_RISE_IN_PERCENTS:
            return

        notifier.slack_message(
            message=MESSAGE.format(rise=rise, views=views_per_interval),
            channel="#tests",
            app_name="Pageviews check",
        )
