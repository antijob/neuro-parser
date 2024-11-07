from django.contrib import admin

from server.apps.core.admins.actions.activate_source_action import activate_source
from server.apps.core.admins.actions.deactivate_source_action import (
    deactivate_source,
)
from server.apps.core.admins.actions.disable_models_action import disable_models
from server.apps.core.admins.actions.downvoted_incident_action import (
    downvoted_incidents,
)
from server.apps.core.admins.actions.enable_models_action import enable_models
from server.apps.core.admins.actions.export_incidents_as_csv_action import (
    export_incidents_as_csv,
)
from server.apps.core.admins.filters.downvote_filter import DownvoteFilter
from server.apps.core.forms import IncidentTypeForm, SourceForm
from server.apps.core.models import (
    Article,
    Country,
    IncidentType,
    MediaIncident,
    Region,
    Proxy,
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "country")


@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display = ("description", "model_path", "is_active")
    form = IncidentTypeForm
    actions = [disable_models, enable_models]


@admin.register(MediaIncident)
class MediaIncidentAdmin(admin.ModelAdmin):
    list_display = (
        "any_title",
        "incident_type",
        "create_date",
        "status",
        "downvote",
        "rate_article",
    )
    autocomplete_fields = ["related_article", "duplicate"]
    list_filter = ["status", "incident_type", DownvoteFilter]
    actions = [export_incidents_as_csv, downvoted_incidents]
    search_fields = ["title"]

    def rate_article(self, obj):
        if obj.related_article:
            return obj.related_article.rate

    rate_article.short_description = "Article rate"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "url",
        "create_date",
        "publication_date",
        "create_date",
        "title",
        "is_downloaded",
        "is_parsed",
        "is_duplicate",
        "is_redirect",
        "rate",
    )
    ordering = ("-create_date",)
    actions = ["force_parse"]
    search_fields = ["url", "title"]

    def force_parse(self, request, queryset):
        for obj in queryset:
            obj.is_parsed = False
            obj.save()
        self.message_user(request, f"{queryset.count()} articles will be parsed.")

    force_parse.short_description = "Force parse"


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    form = SourceForm
    list_display = ("url", "country", "region", "is_active")
    actions = [deactivate_source, activate_source]
    search_fields = ["url"]

    # TODO: найти лучший вариант для сохранения списка источников
    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
        else:
            urls = obj.url.split()
            for url in urls:
                if not url:
                    continue
                if Source.objects.filter(url=url).exists():
                    continue

                new_source = Source(
                    url=url,
                    is_active=obj.is_active,
                    country=obj.country,
                    region=obj.region,
                )
                new_source.save()


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = ("ip", "port", "country", "is_active")
