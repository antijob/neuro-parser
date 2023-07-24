# -*- coding: utf-8 -*-

from dateutil.rrule import DAILY, MONTHLY, rrule
from django.db.models import Count, Q, Sum
from django.db.models.functions import Trunc
from django.utils import timezone

from .united_incidents import UnitedTablesData
from server.apps.core.models import MediaIncident, Tag


class ChartData(UnitedTablesData):
    SCALE_DAYS = 0
    SCALE_MONTHS = 1
    SCALE_NAMES = ["day", "month"]

    def line_chart_data(self, start_date, end_date):
        days_range = (end_date - start_date).days
        if days_range > 60:
            scale = self.SCALE_MONTHS
        else:
            scale = self.SCALE_DAYS

        scale_name = self.SCALE_NAMES[scale]
        filtered_querysets = [
            self._filter(model) for model in self.incident_models
        ]
        annotated_querysets = [
            self._annotate_line_chart_data(incidents, scale_name)
            for incidents in filtered_querysets
        ]
        incidents = self._union(annotated_querysets)
        chart_data = dict(incidents.values_list("date_tick", "total"))

        # add zeros for ticks with no page views
        freq = (DAILY, MONTHLY)[scale]
        if freq == MONTHLY:
            start_date = start_date.replace(day=1)
        naive_ticks = rrule(freq=freq, dtstart=start_date, until=end_date)
        ticks = map(timezone.make_aware, naive_ticks)
        chart_data_with_zeros = []
        chart_data_labels = []
        for tick in ticks:
            chart_data_with_zeros += [chart_data.get(tick.date(), 0)]
            chart_data_labels += [tick.timestamp()]

        return {
            "chart_data": chart_data_with_zeros,
            "chart_data_labels": chart_data_labels,
            "scale": scale,
        }

    def pie_chart_data(self, slice_by="incident_type"):
        filtered_querysets = [
            self._filter(model) for model in self.incident_models
        ]
        annotated_querysets = [
            self._annotate_pie_chart_data(incidents, slice_by)
            for incidents in filtered_querysets
        ]

        if slice_by == "incident_type":
            category_counters = self._union(annotated_querysets).order_by(
                "incident_type"
            )
            category_summs = {}
            for (category, counter) in category_counters:
                category_summs[category] = (
                    category_summs.get(category, 0) + counter
                )
            if category_summs:
                categories, data = zip(*category_summs.items())
                labels = list(IncidentType.objects.filter(id__in=categories).values_list('description', flat=True))
            else:
                categories = []
                data = []
                labels = []
        else:
            tags = Tag.objects.filter(is_active=True)
            incidents = self._union(annotated_querysets).aggregate(
                **{tag.name: Sum("tag_%d" % tag.pk) for tag in tags}
            )
            tags_and_counters = list(zip(*incidents.items()))
            labels, counters = tags_and_counters
            data = [(counter or 0) for counter in counters]
        return {
            "chart_data": data,
            "chart_data_labels": labels,
        }

    def _annotate_line_chart_data(self, incidents, scale_name):
        incidents = (
            incidents.annotate(date_tick=Trunc("create_date", scale_name))
            .values("date_tick")
            .order_by("date_tick")
            .annotate(total=Count("id"))
        )
        return incidents

    def _annotate_pie_chart_data(self, incidents, slice_by):
        if slice_by == "incident_type":
            return self._annotate_pie_chart_by_category_data(incidents)
        else:
            return self._annotate_pie_chart_by_tag_data(incidents)

    def _annotate_pie_chart_by_category_data(self, incidents):
        incidents = (
            incidents.values("incident_type")
            .annotate(slice_counter=Sum("count"))
            .values_list("incident_type", "slice_counter")
            .order_by("incident_type")
        )
        return incidents

    def _annotate_pie_chart_by_tag_data(self, incidents):
        tags = Tag.objects.filter(is_active=True)
        for tag in tags:
            incidents = incidents.annotate(
                **{
                    "tag_%d"
                    % tag.pk: Sum("count", filter=Q(tags__contains=[tag.name]))
                }
            )
        return incidents
