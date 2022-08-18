from dateutil.rrule import DAILY, HOURLY, MONTHLY, rrule
from django.db.models import Avg, Count
from django.db.models.functions import Trunc
from django.utils import timezone
from tracking.models import Pageview, Visitor


def pageviews_for_url(url):
    return Pageview.objects.filter(url=url) if url else Pageview.objects


def visitors_for_url(url):
    return Visitor.objects.filter(pageviews__url=url) if url else Visitor.objects


def filter_by_date_range(pageviews, start_date, end_date):
    end_date_next = end_date + timezone.timedelta(days=1)
    return pageviews.filter(view_time__date__range=(start_date, end_date_next))


def visitor_stats(visitors, start_dt, end_dt):
    visitors = visitors.filter(start_time__date__gte=start_dt,
                               start_time__date__lte=end_dt)
    stats = {
        "total": 0,
        "unique": 0,
    }
    stats["total"] = visitors.values("pageviews__visitor").distinct().count()
    if not stats["total"]:
        return stats

    stats["pages_per_visit"] = (
        visitors.annotate(page_count=Count("pageviews"))
        .filter(page_count__gt=0)
    )
    return stats


def pageview_stats(pageviews):
    stats = {
        "total": 0,
    }
    stats["total"] = pageviews.count()
    if not stats["total"]:
        return stats

    return stats


def chart_data(pageviews, start, end):
    SCALE_HOURS = 0
    SCALE_DAYS = 1
    SCALE_MONTHS = 2
    SCALE_NAMES = ["hour", "day", "month"]

    end = end + timezone.timedelta(days=1)
    days_range = (end - start).days
    if days_range > 60:
        scale = SCALE_MONTHS
    elif days_range > 3:
        scale = SCALE_DAYS
    else:
        scale = SCALE_HOURS

    scale_name = SCALE_NAMES[scale]
    chart_data = (
        pageviews.annotate(date_tick=Trunc("view_time", scale_name))
        .values("date_tick")
        .order_by("date_tick")
        .annotate(total=Count("id"))
    )
    chart_data = dict(chart_data.values_list("date_tick", "total"))

    # add zeros for ticks with no page views
    freq = (HOURLY, DAILY, MONTHLY)[scale]
    if freq == MONTHLY:
        start = start.replace(day=1)
    naive_ticks = rrule(freq=freq, dtstart=start, until=end)
    ticks = map(timezone.make_aware, (naive_ticks))
    chart_data_with_zeros = []
    chart_data_labels = []
    table_row_headers = []
    for tick in ticks:
        chart_data_with_zeros += [chart_data.get(tick, 0)]
        chart_data_labels += [tick.timestamp()]
        if scale == SCALE_HOURS:
            table_row_headers += [tick.hour]
        elif scale == SCALE_DAYS:
            table_row_headers += [tick.day]
        elif scale == SCALE_MONTHS:
            table_row_headers += [tick.strftime("%B")]

    return {
        "chart_data": chart_data_with_zeros,
        "chart_data_labels": chart_data_labels,
        "table_row_headers": table_row_headers,
        "scale": scale,
    }


def referer_stats(pageviews):
    return (
        pageviews.exclude(referer__isnull=True)
        .values("referer")
        .annotate(total=Count("referer"))
        .order_by("-total")
    )


def url_stats(pageviews):
    return pageviews.values("url").annotate(total=Count("url")).order_by("-total")
