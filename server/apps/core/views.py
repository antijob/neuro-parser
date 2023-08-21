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

from server.apps.core.forms import (
    CampaignForm,
    CampaignPageForm,
    ContactForm,
    ExplanationForm,
    IncidentCreateForm,
    MediaIncidentCreateForm,
    MediaIncidentUpdateForm,
    PostForm,
    StageForm,
    TagForm,
    CampaignIncidentForm,
    UserIncidentCreateForm,
    UserIncidentUpdateForm)
from server.apps.core.logic import map_data, counters
from server.apps.core.logic.grabber.compare import rate_articles
from server.apps.core.logic.united_incidents import UnitedTablesData
from server.apps.core.models import (
    Article,
    Campaign,
    CampaignPage,
    Document,
    Explanation,
    IncidentType,
    MediaIncident,
    MediaIncidentFile,
    Post,
    Source,
    Stage,
    Tag,
    UserIncident,
    DataLeak,
    UserIncidentFile,
)
from server.apps.core.logic.charts import ChartData
from server.apps.core.logic.email import send_email
from server.apps.core.tasks import apply_tag_task, search_duplicates
from server.apps.users.forms import UserForm
from server.apps.users.models import User


class DataLeakSearchView(generic.View):
    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone', None)
        if phone is not None:
            try:
                DataLeak.objects.get(phone=phone)
                return JsonResponse({"status": "ok"})
            except DataLeak.DoesNotExist:
                pass
        return JsonResponse({"status": "not found"})


class ContactFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'contact_form': ContactForm(),
        })
        return context


class MapDataView(generic.View):
    def get(self, request, *args, **kwargs):
        today = timezone.datetime.now().date()
        long_time_ago = timezone.datetime(2000, 1, 1).date()
        start = self.request.GET.get('start') or long_time_ago
        end = self.request.GET.get('end') or today
        category = self.request.GET.get('category')
        tag = self.request.GET.get('tag')
        incident_map_data = map_data.incident_map_data(start, end, category, tag)
        data = {'map_data': incident_map_data}
        return JsonResponse(data)


class FilterDataView(generic.View):
    def get(self, request, *args, **kwargs):
        sorted_regions = (MediaIncident.REGIONS[:1] +
                          sorted(MediaIncident.REGIONS[1:],
                                 key=lambda x: x[1]))
        regions = list(map(list, sorted_regions))
        regions[0] = ['', regions[0][1]]
        tags = list(Tag.objects
                    .filter(is_active=True)
                    .values_list('name', flat=True))
        data = {'incident_type_names': self.incident_type_names,
                'regions': regions,
                'tags': tags}
        return JsonResponse(data)


class IncidentsTableDataView(generic.View):
    def get(self, request, *args, **kwargs):
        search_string = request.GET.get('search[value]')
        region = request.GET.get('region')
        tag = request.GET.get('tag')
        category = int(request.GET.get('category', -1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        long_time_ago = '2001-01-01'
        start_date = self.request.GET.get('start_date') or long_time_ago
        today = timezone.datetime.now().date().strftime('%Y-%m-%d')
        end_date = self.request.GET.get('end_date') or today
        data = (UnitedTablesData()
                .public_only()
                .exclude_private_data()
                .exclude_campaign_incidents()
                .from_region(region)
                .search_tag(tag)
                .filter_by_category(category)
                .filter_by_date_range(start_date, end_date)
                .search_string(search_string)
                .page(start, length)
                .fetch())
        return JsonResponse(data)


class LineChartDataView(generic.View):
    def get(self, request, *args, **kwargs):
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        region = request.GET.get("region")
        category = int(request.GET.get("category") or -1)
        tag = request.GET.get("tag")
        start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
        chart_data = (
            ChartData()
                .public_only()
                .from_region(region)
                .search_tag(tag)
                .filter_by_category(category)
                .filter_by_date_range(start_date_str, end_date_str)
                .line_chart_data(start_date, end_date)
        )
        return JsonResponse(chart_data)


class PieChartDataView(generic.View):
    def get(self, request, *args, **kwargs):
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        slice_by = request.GET.get("slice_by")
        region = request.GET.get("region")
        chart_data = (
            ChartData()
                .public_only()
                .from_region(region)
                .filter_by_date_range(start_date_str, end_date_str)
                .pie_chart_data(slice_by=slice_by)
        )
        return JsonResponse(chart_data)



class DashboardMixin(LoginRequiredMixin):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # context['assigned_incidents'] = counters.count_assigned_incidents(self.request.user)
        # context['unprocessed_mediaincidents'] = counters.count_unprocessed_mediaincidents()
        return context


class DashboardView(DashboardMixin, generic.TemplateView):
    """Dashboard main page"""

    template_name = 'core/dashboard/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'user_incidents': counters.count_userincidents(),
            'unprocessed_userincidents': counters.count_unprocessed_userincidents(),
            'media_incidents': counters.count_mediaincidents()
        })
        return context


class DashboardIncidentFileUploadMixin():
    file_model = None

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        files = self.request.FILES.getlist('files')
        if files:
            for file in files:
                self.file_model.objects.create(file=file,
                                               incident=self.object)

        # Delete files
        file_pks = [int(pk) for pk in self.request.POST.getlist('delete_file')]
        if file_pks:
            self.file_model.objects.filter(pk__in=file_pks).delete()

        return redirect(self.get_success_url())


class DashboardIncidentCreateView(DashboardMixin,
                                  DashboardIncidentFileUploadMixin,
                                  generic.CreateView):
    model = UserIncident
    form_class = UserIncidentCreateForm
    context_object_name = 'incident'
    template_name = 'core/dashboard/dashboard_incident_create.html'
    success_url = reverse_lazy('core:dashboard-incidents')
    file_model = UserIncidentFile


class DashboardMediaIncidentCreateView(DashboardMixin,
                                       DashboardIncidentFileUploadMixin,
                                       generic.CreateView):
    model = MediaIncident
    form_class = MediaIncidentCreateForm
    context_object_name = 'incident'
    template_name = 'core/dashboard/dashboard_mediaincident_create.html'
    success_url = reverse_lazy('core:dashboard-mediaincidents')
    file_model = MediaIncidentFile


def download_user_incidents_as_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="incidents.csv"'
    writer = csv.writer(response)

    incidents = UserIncident.objects.all()

    writer.writerow(['email', 'messenger_username', 'description'])
    for incident in incidents:
        writer.writerow([
            incident.applicant_email,
            incident.applicant_messenger,
            incident.description,
        ])

    return response


class DashboardIncidentsView(DashboardMixin, generic.TemplateView):
    template_name = 'core/dashboard/dashboard_incidents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table_settings = {
            'status_code': None,
            'mediaincidents_only': None,
            'userincidents_only': None,
            'active_status': None,
            'assigned_only': None,
            'show_deleted': None,
            'table_title': 'Все инциденты'}
        stat_data = {
            'user_incidents': counters.count_userincidents(),
            'unprocessed_userincidents':
                counters.count_unprocessed_userincidents(),
            'unprocessed_mediaincidents':
                counters.count_unprocessed_mediaincidents(),
            'media_incidents': counters.count_mediaincidents()}
        context.update(table_settings)
        context.update(stat_data)
        return context


class DashboardProcessedIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_status'] = 1
        context['table_title'] = 'Инциденты в работе'
        return context


class DashboardUnprocessedIncidentsView(DashboardIncidentsView):
    template_name = 'core/dashboard/dashboard_campaign_incidents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = 0
        context['table_title'] = 'Необработанные инциденты'
        return context


class DashboardMediaIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mediaincidents_only'] = 1
        context['table_title'] = 'Все инциденты из СМИ'
        return context


class DashboardUserIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['userincidents_only'] = 1
        context['table_title'] = 'Все заявки'
        return context


class DashboardUnprocessedUserIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = 0
        context['userincidents_only'] = 1
        context['table_title'] = 'Необработанные заявки'
        return context


class DashboardUnprocessedMediaIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = 0
        context['mediaincidents_only'] = 1
        context['table_title'] = 'Необработанные инциденты из СМИ'
        return context


class DashboardRejectedUserIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = 1
        context['userincidents_only'] = 1
        context['table_title'] = 'Отклоненные заявки'
        return context


class DashboardRejectedMediaIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = 1
        context['mediaincidents_only'] = 1
        context['table_title'] = 'Отклоненные инциденты из СМИ'
        return context


class DashboardAssignedIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_title'] = 'Мои инциденты'
        context['active_status'] = 1
        context['assigned_only'] = 1
        return context


class DashboardAcceptedUserIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = UserIncident.PROCESSED_AND_ACCEPTED
        context['userincidents_only'] = 1
        context['table_title'] = 'Принятые заявки'
        return context


class DashboardAcceptedMediaIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = MediaIncident.PROCESSED_AND_ACCEPTED
        context['mediaincidents_only'] = 1
        context['table_title'] = 'Принятые из СМИ'
        return context


class DashboardInProgressUserIncidentsView(DashboardIncidentsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = UserIncident.IN_PROGRESS
        context['userincidents_only'] = 1
        context['table_title'] = 'Заявки в работе'
        return context


class DashboardIncidentsTableDataView(DashboardMixin, generic.ListView):
    def get(self, request, *args, **kwargs):
        search_string = request.GET.get('search[value]')
        region = request.GET.get('region')
        category = int(request.GET.get('category') or -1)
        status_code = request.GET.get('status_code')
        status_code = int(status_code) if status_code and status_code.isdigit() else None
        mediaincidents_only = request.GET.get('mediaincidents_only')
        mediaincidents_only = (int(mediaincidents_only)
                               if mediaincidents_only and mediaincidents_only.isdigit()
                               else None)
        userincidents_only = request.GET.get('userincidents_only')
        userincidents_only = (int(userincidents_only)
                              if userincidents_only and userincidents_only.isdigit()
                              else None)
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        assigned_to = request.user if request.GET.get('assigned_only') else None
        with_active_status = request.GET.get('active_status')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        show_deleted = request.GET.get('show_deleted')
        show_deleted = (int(show_deleted)
                        if show_deleted and show_deleted.isdigit()
                        else None)
        data = (UnitedTablesData()
                .mediaincidents_only(mediaincidents_only)
                .userincidents_only(userincidents_only)
                .assigned_to(assigned_to)
                .with_status(status_code)
                .with_active_status(with_active_status)
                .from_region(region)
                .search_string(search_string)
                .filter_by_date_range(start_date, end_date)
                .filter_by_category(category)
                .show_deleted(show_deleted)
                .page(start, length)
                .fetch())
        return JsonResponse(data)


class DashboardIncidentDeleteView(DashboardMixin, generic.DeleteView):
    model = UserIncident
    success_url = reverse_lazy('core:dashboard-incidents')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = obj.DELETED
        obj.save(update_fields=['status'])
        message = 'Заявка #{pk} успешно удалена!'.format(pk=obj.pk)
        messages.success(request, message)
        return redirect(self.success_url)


class DashboardMediaIncidentDeleteView(DashboardMixin, generic.DeleteView):
    model = MediaIncident
    context_object_name = 'incident'
    success_url = reverse_lazy('core:dashboard-incidents')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = obj.DELETED
        obj.save(update_fields=['status'])
        message = 'Заявка #{pk} успешно удалена!'.format(pk=obj.pk)
        messages.success(request, message)
        return redirect(self.success_url)


class IncidentAjaxMixin(LoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.public_title = request.POST.get('public_title', obj.any_title())
        obj.public_description = request.POST.get('public_description',
                                                  obj.any_description())
        obj.region = request.POST.get('region', obj.region)
        obj.count = request.POST.get('count', obj.count)
        obj.create_date = request.POST.get('create_date', obj.create_date)
        tags = request.POST.get('tags')
        if tags is not None:
            obj.tags = tags.split(',')
        obj.incident_type = request.POST.get('category', obj.incident_type)

        status = request.POST.get('status')
        if status is not None:
            status = int(status)
            obj.status = status
            is_authenticated = request.user.is_authenticated
            is_processed = status != UserIncident.UNPROCESSED
            if is_processed and is_authenticated:
                obj.assigned_to = request.user

        obj.save()
        return JsonResponse({'status': 200})


class UserIncidentAjaxUpdateView(IncidentAjaxMixin, generic.View):
    def get_object(self, **kwargs):
        return UserIncident.objects.get(pk=self.kwargs['pk'])


class MediaIncidentAjaxUpdateView(IncidentAjaxMixin, generic.View):
    def get_object(self, **kwargs):
        return MediaIncident.objects.get(pk=self.kwargs['pk'])


class DashboardIncidentUpdateMixin(DashboardMixin,
                                   DashboardIncidentFileUploadMixin,
                                   generic.UpdateView):
    context_object_name = 'incident'
    slug_field = 'pk'
    slug_url_kwarg = 'pk'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['files'] = self.object.files.all()
        return context

    def get_initial(self):
        if not hasattr(self, 'object'):
            return {}
        return {'count': self.object.count,
                'public_title': self.object.any_title,
                'public_description': self.object.any_description}


class DashboardIncidentUpdateView(DashboardIncidentUpdateMixin):
    model = UserIncident
    form_class = UserIncidentUpdateForm
    file_model = UserIncidentFile
    template_name = 'core/dashboard/dashboard_incident_update.html'

    def get_success_url(self):
        return reverse('core:dashboard-incident-update',
                       kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_json'] = json.dumps(self.object.form_data)
        return context


class DashboardMediaIncidentUpdateView(DashboardIncidentUpdateMixin):
    model = MediaIncident
    form_class = MediaIncidentUpdateForm
    file_model = MediaIncidentFile
    template_name = 'core/dashboard/dashboard_mediaincident_update.html'

    def get_success_url(self):
        return reverse('core:dashboard-mediaincident-update',
                       kwargs={'pk': self.kwargs.get('pk')})


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    """Dashboard user detail view"""

    model = User
    slug_field = 'pk'
    slug_url_kwarg = 'pk'
    template_name = 'core/dashboard/dashboard_user_details.html'


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Dashboard user update view"""

    template_name = 'core/dashboard/dashboard_user_update.html'
    form_class = UserForm

    def get_success_url(self):
        return reverse('core:dashboard-user-detail', kwargs={'pk': self.request.user.pk})

    def get_object(self, **kwargs):
        return User.objects.get(pk=self.request.user.pk)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Ошибка при обновлении формы. Пожалуйста, убедитесь, что данные верны',
        )
        return HttpResponseRedirect(reverse('core:dashboard-user-update'))

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Профиль успешно обновлен')
        return HttpResponseRedirect(self.get_success_url())



class CampaignViewMixin(DashboardMixin):
    model = Campaign
    form_class = CampaignForm
    template_name = 'core/dashboard/dashboard_campaign_create.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['incident_form'] = CampaignIncidentForm()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.data.get('generate'):
            form.instance.save()
            if hasattr(form.instance, "document"):
                form.instance.document.template = form.data['document']
                form.instance.document.instruction = form.data['instruction']
            else:
                form.instance.document = Document.objects.create(
                    campaign=form.instance,
                    template=form.data['document'],
                    instruction=form.data['instruction'])
            form.instance.document.save()
        else:
            if hasattr(form.instance, "document"):
                form.instance.document.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:dashboard-campaign-updated',
                       kwargs={'pk': self.object.pk})


class DashboardCampaignCreateView(CampaignViewMixin, generic.CreateView):
    pass


class DashboardCampaignUpdateView(CampaignViewMixin, generic.UpdateView):
    pass


class DashboardCampaignUpdatedView(CampaignViewMixin, generic.UpdateView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['saved'] = "1"
        return context


class DashboardCampaignListView(DashboardMixin, generic.ListView):
    model = Campaign
    context_object_name = 'campaigns'
    template_name = 'core/dashboard/dashboard_campaign_list.html'

    def get_queryset(self):
        return self.model.objects.filter(is_active=True).select_related('author')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Все кампании'
        return context


class DashboardDeletedCampaignListView(DashboardMixin, generic.ListView):
    model = Campaign
    context_object_name = 'campaigns'
    template_name = 'core/dashboard/dashboard_campaign_list.html'

    def get_queryset(self):
        return self.model.objects.filter(is_active=False).select_related('author')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Удаленные кампании'
        return context


class DashboardArticlesView(DashboardView, generic.TemplateView):
    model = Article
    context_object_name = 'articles'
    template_name = 'core/dashboard/dashboard_article_list.html'


class DashboardArticleApproveView(LoginRequiredMixin, generic.UpdateView):
    model = Article
    context_object_name = 'article'
    template_name = 'core/dashboard/dashboard_article_approve.html'
    fields = '__all__'
    colors = ['info', 'success', 'warning', 'danger']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        percents = context['article'].relevance / 8 * 100
        color_index = int(percents * len(self.colors) / 100)
        if color_index >= len(self.colors):
            color_index = len(self.colors) - 1
        elif color_index < 0:
            color_index = 0
        context['color'] = self.colors[color_index]
        context['percents'] = percents
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        approved = request.POST.get('approved')
        if approved is None:
            return HttpResponseBadRequest('Approved parameter required')

        if approved == '1':
            obj.create_incident()
            obj.incident.status = MediaIncident.PROCESSED_AND_ACCEPTED
            obj.incident.assigned_to = request.user
            obj.incident.save()
            search_duplicates.delay(obj.id)
            return HttpResponseRedirect(
                reverse('core:dashboard-mediaincident-update',
                        kwargs={'pk': obj.incident.pk}))
        elif approved == '0':
            obj.relevance = -1
            obj.save()
            return HttpResponseRedirect(reverse('core:dashboard-article-list'))


class ArticleDataView(LoginRequiredMixin, generic.View):
    TRASH_RELEVANCE_TRESHOLD = 0

    def get(self, request, *args, **kwargs):
        search_string = request.GET.get('search[value]')
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        articles = (Article.objects
                    .filter(is_downloaded=True,
                            is_incident_created=False,
                            relevance__gte=self.TRASH_RELEVANCE_TRESHOLD)
                    .exclude(text=''))

        if search_string:
            articles = articles.filter(Q(title__icontains=search_string) |
                                       Q(text__icontains=search_string) |
                                       Q(url__icontains=search_string))

        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
            articles = articles.filter(publication_date__gte=start_date,
                                       publication_date__lte=end_date)
        articles = (articles
                    .values('title', 'url', 'publication_date', 'relevance', 'pk', 'create_date')
                    .order_by('-create_date'))

        page = self.paginate(articles, start, length)
        for article in page:
            article['publication_date'] = article['publication_date'] or article['create_date']

        records_filtered = articles.count()
        response = {'data': list(page), 'recordsFiltered': records_filtered}
        return JsonResponse(response)

    @staticmethod
    def paginate(query, start, length):
        paginator = Paginator(query, length)
        try:
            page = paginator.page(start // length + 1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            page = paginator.page(1)
        return page


class DashboardTagListView(DashboardMixin, generic.ListView):
    model = Tag
    template_name = 'core/dashboard/dashboard_tag_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tags = list(Tag.objects.all().values('name', 'markers', 'create_date', 'is_active', 'pk'))
        context['tags'] = json.dumps(tags, cls=DjangoJSONEncoder)
        context.update({
            'user_incidents': counters.count_userincidents(),
            'unprocessed_userincidents': counters.count_unprocessed_userincidents(),
            'media_incidents': counters.count_mediaincidents()
        })
        return context


class DashboardTagFormMixin(DashboardMixin):
    model = Tag
    form_class = TagForm
    context_object_name = 'tag'
    template_name = 'core/dashboard/dashboard_tag_update.html'

    def get_success_url(self):
        return reverse('core:dashboard-tag-updated',
                       kwargs={'pk': self.object.pk})


class DashboardTagCreateView(DashboardTagFormMixin, generic.CreateView):
    pass


class DashboardTagUpdateView(DashboardTagFormMixin, generic.UpdateView):
    pass


class DashboardTagUpdatedView(DashboardTagFormMixin, generic.UpdateView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.object.is_active:
            apply_tag_task.delay(self.object.pk)
        context['saved'] = "1"
        return context


class DashboardTrashView(DashboardIncidentsView):
    template_name = 'core/dashboard/dashboard_incidents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'status_code': MediaIncident.DELETED,
            'show_deleted': '1',
            'table_title': 'Удаленные инциденты',
        })
        return context


class DashboardPostListView(DashboardMixin, generic.TemplateView):
    template_name = 'core/dashboard/dashboard_posts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_active'] = "1"
        context['title'] = 'Все посты'
        return context


class DashboardDeletedPostListView(DashboardPostListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_active'] = "0"
        context['title'] = 'Удаленные посты'
        return context


class DashboardPostDataView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        search_string = request.GET.get('search[value]')
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        is_active = int(self.request.GET.get('is_active', 1))
        posts = Post.objects.filter(is_active=is_active)

        if search_string:
            posts = posts.filter(Q(title__icontains=search_string) |
                                 Q(text__icontains=search_string))

        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
            posts = posts.filter(publication_date__gte=start_date,
                                 publication_date__lte=end_date)
        posts = (posts
                 .values('title', 'text', 'publication_date', 'create_date',
                         'author__first_name', 'author__last_name', 'pk', 'public')
                 .order_by('-create_date'))

        page = self.paginate(posts, start, length)
        for post in page:
            first_name = post['author__first_name'] or ''
            last_name = post['author__last_name'] or ''
            post['author'] = '{} {}'.format(first_name, last_name)

        records_filtered = posts.count()
        response = {'data': list(page), 'recordsFiltered': records_filtered}
        return JsonResponse(response)

    @staticmethod
    def paginate(query, start, length):
        paginator = Paginator(query, length)
        try:
            page = paginator.page(start // length + 1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            page = paginator.page(1)
        return page


class DashboardPostViewMixin(DashboardMixin):
    model = Post
    form_class = PostForm
    context_object_name = 'post'
    template_name = 'core/dashboard/dashboard_post_create.html'

    def get_success_url(self):
        return reverse('core:dashboard-post-updated',
                       kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Save with author
        form.instance.author = self.request.user
        return super().form_valid(form)


class DashboardPostCreateView(DashboardPostViewMixin, generic.CreateView):
    pass


class DashboardPostUpdateView(DashboardPostViewMixin, generic.UpdateView):
    pass


class DashboardPostUpdatedView(DashboardPostViewMixin, generic.UpdateView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['saved'] = "1"
        return context


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


class ExportTableView(generic.View):

    def get(self, request, *args, **kwargs):
        search_string = request.GET.get('search[value]')
        region = request.GET.get('region')
        tag = request.GET.get('tag')
        category = int(request.GET.get('category', -1))
        long_time_ago = '2001-01-01'
        start_date = self.request.GET.get('start_date') or long_time_ago
        today = timezone.datetime.now().date().strftime('%Y-%m-%d')
        end_date = self.request.GET.get('end_date') or today
        data = (UnitedTablesData()
                .public_only()
                .from_region(region)
                .search_tag(tag)
                .filter_by_category(category)
                .filter_by_date_range(start_date, end_date)
                .search_string(search_string)
                .export())

        content_type = ('application/vnd.openxmlformats-officedocument'
                        '.spreadsheetml.sheet')
        response = HttpResponse(content_type=content_type)
        content_disp = 'attachment; filename="runet_report_table.xlsx"'
        response['Content-Disposition'] = content_disp
        book = Workbook(response, {'in_memory': True})
        sheet = book.add_worksheet('incidents')
        bold_format = book.add_format({'bold': True})
        sheet.write(0, 0, 'Загружено с сайта https://runet.report')
        sheet.write(1, 0, 'Инцидент', bold_format)
        sheet.write(1, 1, 'Регион', bold_format)
        sheet.write(1, 2, 'Ссылка', bold_format)
        sheet.write(1, 3, 'Категория', bold_format)
        sheet.write(1, 4, 'Количество', bold_format)
        sheet.write(1, 5, 'Дата', bold_format)
        date_format = book.add_format({'num_format': 'dd.mm.yyyy'})
        for (row_num, row) in enumerate(data, start=2):
            sheet.write(row_num, 0, row[0])
            sheet.write(row_num, 1, row[1])
            sheet.write_url(row_num, 2, row[2])
            sheet.write(row_num, 3, row[3])
            sheet.write(row_num, 4, row[4])
            sheet.write_datetime(row_num, 5, row[5], date_format)
        book.close()

        return response


class GenerateDocument(generic.View):

    def get(self, request, *args, **kwargs):
        file_format = request.GET.get("f")
        incident_uuid = kwargs.get('incident_uuid')
        incident = get_object_or_404(UserIncident, uuid=incident_uuid)
        document = incident.campaign.document
        html = document.render_html(incident)
        if file_format == "pdf":
            pdf = document.render_pdf(html)
            return HttpResponse(
                pdf,
                content_type="application/pdf; charset=cp1251"
            )
        elif file_format == "docx":
            docx = document.render_docx(html)
            response = HttpResponse(
                docx,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            response["Content-Disposition"] = "attachment; filename=example.docx"
            return response
        return HttpResponse(html)


class DashboardStageFormMixin(LoginRequiredMixin):
    model = Stage
    form_class = StageForm
    template_name = "core/dashboard/dashboard_stage_form.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['campaign_pk'] = self.kwargs.get('campaign_pk')
        return data


class DashboardStageFormCreateView(DashboardStageFormMixin,
                                   generic.View):

    def get(self, request, *args, **kwargs):
        context = {"form": self.form_class(),
                   "campaign_pk": self.kwargs.get("campaign_pk")}
        return render(request, self.template_name, context)


class DashboardStageFormUpdateView(DashboardStageFormMixin,
                                   generic.UpdateView):
    def get_object(self, **kwargs):
        return Stage.objects.get(pk=self.kwargs['stage_pk'])


class DashboardStageUpdateView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        title = request.POST.get("title")
        summary = request.POST.get("summary")
        text = request.POST.get("text")
        campaign_pk = kwargs.get("campaign_pk")
        stage_pk = kwargs.get("stage_pk")
        stage_data = {"title": title,
                      "summary": summary,
                      "text": text}
        if stage_pk:
            stage = Stage.objects.filter(pk=stage_pk).update(**stage_data)
        else:
            stage_data["campaign_id"] = int(campaign_pk)
            stage = Stage.objects.create(**stage_data)
            stage_pk = stage.pk
        return JsonResponse({"stage_pk": stage_pk})


class DashboardStageDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Stage
    success_url = reverse_lazy('core:dashboard-updated')


class DashboardStageSuccessView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('{"status": 200, "message": "ok"}')



class CampaignMapData(generic.View):
    def get(self, request, *args, **kwargs):
        sorted_regions = (MediaIncident.REGIONS[:1] +
                          sorted(MediaIncident.REGIONS[1:],
                                 key=lambda x: x[1]))
        regions = list(map(list, sorted_regions))
        pk = kwargs.get("pk")
        slug = kwargs.get("slug")
        if pk:
            campaign = Campaign.objects.get(pk=pk)
        elif slug:
            campaign = Campaign.objects.get(slug=slug)
        else:
            raise Http404
        campaign_map_data = (map_data.campaign_map_data(campaign))
        campaign_map_data = list(campaign_map_data)
        return JsonResponse({"map_data": campaign_map_data,
                             "regions": regions,
                             "chart_description": campaign.chart_description})


class DashboardExplanationFormMixin(LoginRequiredMixin):
    model = Explanation
    form_class = ExplanationForm
    template_name = "core/dashboard/dashboard_explanation_form.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['campaign_pk'] = self.kwargs.get('campaign_pk')
        return data


class DashboardExplanationFormCreateView(
    DashboardExplanationFormMixin, generic.View
):

    def get(self, request, *args, **kwargs):
        context = {"form": self.form_class(),
                   "campaign_pk": self.kwargs.get("campaign_pk")}
        return render(request, self.template_name, context)


class DashboardExplanationFormUpdateView(
    DashboardExplanationFormMixin, generic.UpdateView
):
    def get_object(self, **kwargs):
        return Explanation.objects.get(pk=self.kwargs['explanation_pk'])


class DashboardExplanationUpdateView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        title = request.POST.get("title")
        emphasized = request.POST.get("emphasized") == "true"
        text = request.POST.get("text")
        campaign_pk = kwargs.get("campaign_pk")
        explanation_pk = kwargs.get("explanation_pk")
        explanation_data = {
            "title": title,
            "text": text,
            "emphasized": emphasized}
        if explanation_pk:
            explanation = (
                Explanation.objects
                    .filter(pk=explanation_pk)
                    .update(**explanation_data)
            )
        else:
            explanation_data["campaign_id"] = int(campaign_pk)
            explanation = Explanation.objects.create(**explanation_data)
            explanation_pk = explanation.pk
        return JsonResponse({"explanation_pk": explanation_pk})


class DashboardExplanationDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Explanation
    success_url = reverse_lazy('core:dashboard-updated')


class DashboardExplanationSuccessView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('{"status": 200, "message": "ok"}')


class DashboardCampaignPageViewMixin(DashboardMixin):
    model = CampaignPage
    form_class = CampaignPageForm
    context_object_name = 'page'
    template_name = 'core/dashboard/dashboard_campaign_page.html'

    def get_success_url(self):
        return reverse('core:dashboard-campaign-page-update',
                       kwargs={'pk': self.object.pk})


class DashboardCampaignPageCreateView(DashboardCampaignPageViewMixin,
                                      generic.CreateView):
    pass


class DashboardCampaignPageUpdateView(DashboardCampaignPageViewMixin,
                                      generic.UpdateView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if not context.get("form"):
            context["form"] = CampaignIncidentForm(
                initial={"campaign": context["campaign"].pk}
            )
        return context


class DashboardCampaignPageUpdatedView(DashboardCampaignPageViewMixin,
                                       generic.UpdateView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['saved'] = "1"
        return context


class DashboardCampaignIncidentsListView(DashboardMixin, generic.DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'core/dashboard/dashboard_campaign_incidents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incidents_count'] = context['campaign'].incidents.count()
        table_settings = {
            'table_title': 'Заявки кампании {}'.format(context['campaign'].name)}
        stat_data = {
            'user_incidents': counters.count_userincidents(),
            'unprocessed_userincidents':
                counters.count_unprocessed_userincidents(),
            'unprocessed_mediaincidents':
                counters.count_unprocessed_mediaincidents(),
            'media_incidents': counters.count_mediaincidents()}
        context.update(table_settings)
        context.update(stat_data)
        return context


class DashboardCampaignIncidentsDataView(DashboardMixin, generic.ListView):

    def get(self, request, *args, **kwargs):
        search_string = request.GET.get('search[value]')
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        campaign_pk = kwargs.get('pk')
        data = (UnitedTablesData()
                .userincidents_only()
                .search_string(search_string)
                .filter_by_campaign_pk(campaign_pk)
                .filter_by_date_range(start_date, end_date)
                .page(start, length)
                .fetch())
        return JsonResponse(data)


class DashboardCampaignIncidentsExportView(generic.View):

    def get(self, request, *args, **kwargs):
        campaign_pk = self.kwargs.get('pk')
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        search_string = request.GET.get('search[value]')
        long_time_ago = '2001-01-01'
        start_date = self.request.GET.get('start_date') or long_time_ago
        today = timezone.datetime.now().date().strftime('%Y-%m-%d')
        end_date = self.request.GET.get('end_date') or today
        data = (UnitedTablesData()
                .userincidents_only()
                .filter_by_campaign_pk(campaign_pk)
                .filter_by_date_range(start_date, end_date)
                .search_string(search_string)
                .export_campaign_incidents())

        content_type = ('application/vnd.openxmlformats-officedocument'
                        '.spreadsheetml.sheet')
        response = HttpResponse(content_type=content_type)
        content_disp = 'attachment; filename="campaign_data.xlsx"'
        response['Content-Disposition'] = content_disp
        book = Workbook(response, {'in_memory': True})
        sheet = book.add_worksheet('incidents')
        bold_format = book.add_format({'bold': True})
        sheet.write(0, 0, 'Данные кампании {}'.format(campaign.name))
        sheet.write(1, 0, 'Email', bold_format)
        sheet.write(1, 1, 'Дата', bold_format)
        date_format = book.add_format({'num_format': 'dd.mm.yyyy'})
        for (row_num, row) in enumerate(data, start=2):
            sheet.write(row_num, 0, row[0])
            sheet.write_datetime(row_num, 1, row[1], date_format)
        book.close()

        return response
