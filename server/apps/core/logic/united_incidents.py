from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import CharField, F, IntegerField, Q, Value
from django.utils import timezone

from server.apps.core.models import MediaIncident, UserIncident


class UnitedTablesData:
    """A class used to build query and fetch united incident tables data"""

    VALUES = ('title',
              'public_title',
              'description',
              'public_description',
              'status',
              'assigned_to',
              'assigned_to__first_name',
              'assigned_to__last_name',
              'create_date',
              'region',
              'urls',
              'tags',
              'count',
              'email',
              'incident_type',
              'duplicate_pks',
              'duplicate_titles',
              'original_pk',
              'original_title',
              'pk')

    SAFE_VALUES = (
        'public_title',
        'title',
        'description',
        'region',
        'urls',
        'tags',
        'count',
        'incident_type',
        'create_date',
        'pk',
    )

    def __init__(self):
        self.incident_models = [MediaIncident, UserIncident]
        self.start = 0
        self.length = 10
        self.filter_args = []
        self.filter_kwargs = {}
        self.values = self.VALUES
        self.exclude_private = False
        self.exclude_campaigns = False

    def assigned_to(self, user):
        if user:
            self.filter_kwargs.update(assigned_to=user)
        return self

    def export(self):
        queries_list = [self._filter(model)
                        for model in self.incident_models]
        incidents_union = self._union(queries_list).order_by('-create_date', '-pk')
        regions = dict(MediaIncident.REGIONS)
        for row in incidents_union:
            title = (
                row["public_title"] or
                (row["public_description"] and
                 row["public_description"][:200])
            )
            region = regions.get(row["region"], regions["RU"])
            url = (row["urls"][0]
                   if row["urls"]
                   else "")
            category = dict(MediaIncident.INCIDENT_TYPES)[row["incident_type"]]
            count = row["count"]
            date = row["create_date"]
            yield (title, region, url, category, count, date)

    def export_campaign_incidents(self):
        queries_list = [self._filter(model)
                        for model in self.incident_models]
        incidents_union = self._union(queries_list).order_by('-create_date', '-pk')
        for row in incidents_union:
            yield (row["email"], row["create_date"])

    def fetch(self):
        """Return data fetched with built query"""

        queries_list = [self._filter(model)
                        for model in self.incident_models]
        incidents_union = self._union(queries_list).order_by('-create_date', '-pk')
        page = self._paginate(incidents_union)
        page = self._additional_annotates(page)
        records_filtered = incidents_union.count()
        return {'data': page, 'recordsFiltered': records_filtered}

    def filter_by_date_range(self, start_date, end_date):
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
            self.filter_kwargs.update(create_date__gte=start_date,
                                      create_date__lte=end_date)
        return self

    def from_region(self, region):
        if region and region != "RU":
            self.filter_kwargs.update(region=region)
        # else:
        #     self.filter_kwargs.update(region="RU")
        return self

    def mediaincidents_only(self, mediaincidents_only=True):
        if mediaincidents_only:
            self.incident_models = [MediaIncident]
        return self

    def userincidents_only(self, userincidents_only=True):
        if userincidents_only:
            self.incident_models = [UserIncident]
        return self

    def filter_by_campaign_pk(self, campaign_pk):
        if campaign_pk:
            self.filter_kwargs.update(campaign__pk=campaign_pk)
        return self

    def exclude_campaign_incidents(self, exclude_campaign_incidents=True):
        self.exclude_campaigns = exclude_campaign_incidents
        return self

    def exclude_private_data(self, exclude_private_data=True):
        if exclude_private_data:
            self.values = self.SAFE_VALUES
            self.exclude_private = True
        return self

    def page(self, start=None, length=None):
        self.start = start if start is not None else self.start
        self.length = length if length is not None else self.length
        return self

    def public_only(self, public_only=True):
        if public_only:
            self.filter_kwargs.update(status__in=UserIncident.PUBLIC_STATUSES)
        return self

    def search_string(self, string):
        string = (string or "").strip()
        if not string:
            return self
        if string.startswith("#"):
            return self.search_tag(string.lstrip("#"))

        self.filter_args.append(
            Q(title__icontains=string) |
            Q(description__icontains=string) |
            Q(public_title__icontains=string) |
            Q(public_description__icontains=string))
        return self

    def search_tag(self, tag):
        if tag:
            self.filter_args.append(Q(tags__contains=[tag]))
        return self

    def filter_by_category(self, category):
        if category >= 0:
            self.filter_args.append(Q(incident_type=category))
        return self

    def with_active_status(self, is_active=True):
        if is_active:
            self.filter_kwargs.update(status__in=UserIncident.ACTIVE_STATUSES)
        return self

    def with_status(self, status):
        if status is not None:
            self.filter_kwargs.update(status=status)
        return self

    def show_deleted(self, show):
        if not show:
            self.filter_args.append(~Q(status=UserIncident.DELETED))
        return self

    def _additional_annotates(self, incidents):
        for incident in incidents:
            incident['region_display'] = dict(
                MediaIncident.REGIONS).get(incident['region'])
            if incident['is_media'] or not self.exclude_private:
                incident['any_title'] = (
                    incident['public_title'] or
                    incident['title'] or
                    (incident['description'] and incident['description']))
            else:
                incident['any_title'] = incident['public_title']
            if self.exclude_private:
                del incident['title']
                del incident['description']
                continue

            incident['status_display'] = dict(
                MediaIncident.STATUSES).get(incident['status'])
            if incident['assigned_to']:
                incident['user'] = "{} {}".format(
                    incident.pop('assigned_to__first_name'),
                    incident.pop('assigned_to__last_name'))
            else:
                incident['user'] = ''
        return incidents

    def _filter(self, model):
        """Apply filter args and kwargs to given model data"""
        incidents = model.objects \
            .filter(*self.filter_args, **self.filter_kwargs)
        is_media = issubclass(model, MediaIncident)
        if is_media:
            values = (
                incidents
                .annotate(duplicate_pks=ArrayAgg('duplicates__pk'))
                .annotate(duplicate_titles=ArrayAgg('duplicates__title'))
                .annotate(original_pk=F('duplicate__pk'))
                .annotate(original_title=F('duplicate__title'))
                .annotate(email=Value(
                    "", CharField(max_length=1, null=True)))
                .values(*self.values))
        else:
            if self.exclude_campaigns:
                incidents = incidents.filter(campaign__isnull=True)
            values = (
                incidents
                .annotate(duplicate_pks=Value(
                    [], ArrayField(IntegerField(null=True))))
                .annotate(duplicate_titles=Value(
                    [], ArrayField(CharField(max_length=1, null=True))))
                .annotate(original_pk=Value(
                    None, IntegerField(null=True)))
                .annotate(original_title=Value(
                    "", CharField(max_length=1, null=True)))
                .annotate(email=F('applicant_email'))
                .values(*self.values))
        return values.annotate(is_media=Value(is_media, IntegerField()))

    def _paginate(self, query):
        paginator = Paginator(query, self.length)
        try:
            page = paginator.page(self.start // self.length + 1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            page = paginator.page(1)
        return list(page)

    @staticmethod
    def _union(queries):
        union = queries[0]
        for query in queries[1:]:
            union = union.union(query)
        return union
