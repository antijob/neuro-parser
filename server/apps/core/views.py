# -*- coding: utf-8 -*-
import json
import csv
from xlsxwriter.workbook import Workbook

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Count
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
    Http404)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import strip_tags
from django.views import generic

from server.apps.core.logic import map_data, counters
from server.apps.core.logic.grabber.compare import rate_articles
from server.apps.core.logic.united_incidents import UnitedTablesData
from server.apps.core.models import (
    Article,
    Campaign,
    CampaignPage,
    Explanation,
    IncidentType,
    MediaIncident,
    Source,
    UserIncident,

)
from server.apps.core.logic.charts import ChartData
from server.apps.core.logic.email import send_email
from server.apps.core.tasks import apply_tag_task, search_duplicates
from server.apps.users.models import User


class GrabberAlogrithmsView(LoginRequiredMixin, generic.TemplateView):
    template_name = "core/grabber/algorithms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sources = Source.objects.filter(is_active=True).order_by('url').values('id', 'url')
        context.update({'sources': sources})
        context.update({'algorithms': Source.ALGORITHMS})
        return context

    def post(self, request, *args, **kwargs):
        algorithm = request.POST.get('algorithm')
        source_id = request.POST.get('source')
        if not source_id or not algorithm:
            return JsonResponse({'Algorithm and source are required'}, status=422)
        Source.objects.filter(id=source_id).update(algorithm=algorithm)
        return JsonResponse({"status": 200})


class GrabberAlgorithmsDataView(generic.View):
    def get(self, request, *args, **kwargs):
        source_id = request.GET.get('source')
        if not source_id:
            return JsonResponse({'data': []})
        today = timezone.datetime.now().date()
        date = request.GET.get('date') or today
        articles = (Article.objects
                    .filter(publication_date=date,
                            source_id=source_id,
                            is_downloaded=True)
                    .exclude(text=''))
        data = {}
        data['rates'] = rate_articles(articles)
        source = Source.objects.get(id=source_id)
        data['source_url'] = source.url
        data['algorithm'] = source.algorithm
        return JsonResponse({"data": data})


class GrabberSourceStatisticsView(LoginRequiredMixin, generic.TemplateView):
    template_name = "core/grabber/source_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        week_ago = now - timezone.timedelta(days=7)
        date_filter = Q(articles__publication_date__range=[week_ago, now])
        incidents_filter = Q(articles__is_incident_created=True)
        sources = (Source.objects
                   .filter(is_active=True)
                   .annotate(articles_by_week=Count('articles',
                                                    filter=date_filter))
                   .annotate(all_articles=Count('articles'))
                   .annotate(all_incidents=Count('articles',
                                                 filter=incidents_filter))
                   .order_by('articles_by_week', 'all_articles'))
        context.update({'sources': sources})
        return context
