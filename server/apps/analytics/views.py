from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.views import generic

from .forms import DashboardForm
from .logic import statistics


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "analytics/dashboard.html"
    TOPS_LENGTH = 10

    def get_context_data(self, *args, **kwargs):
        """Returns analytics page context."""

        context = super().get_context_data(*args, **kwargs)

        # Get form data and clean it
        form = DashboardForm(self.request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest("Form invalid")
        url = form.cleaned_data["url"]
        start = form.cleaned_data["start"]
        end = form.cleaned_data["end"]
        form = DashboardForm(
            initial={"start": start, "end": end, "url": url}
        )

        # Get stats data
        pageviews = statistics.pageviews_for_url(url)
        pageviews_in_range = statistics.filter_by_date_range(
            pageviews, start, end
        )
        pageview_stats = statistics.pageview_stats(pageviews_in_range)
        referer_stats = statistics.referer_stats(pageviews_in_range)[: self.TOPS_LENGTH]

        context.update(
            {
                "form": form,
                "pageview_stats": pageview_stats,
                "referer_stats": referer_stats,
                "start": start,
                "end": end
            }
        )
        chart_data = statistics.chart_data(pageviews_in_range, start, end)
        context.update(chart_data)

        table_data = list(zip(chart_data['table_row_headers'],
                              chart_data['chart_data']))
        scale_name = ['Час', 'День', 'Месяц'][chart_data['scale']]
        context.update({"table_data": table_data,
                        "scale_name": scale_name})
        return context
