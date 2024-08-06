# -*- coding: utf-8 -*-

from django.contrib import admin

from server.apps.core.models import (
    Article,
    MediaIncident,
    Source,
    IncidentType,
    Country,
    Region,
)
from server.apps.core.forms import IncidentTypeForm


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
    actions = ["disable_models", "enable_models"]

    def disable_models(self, request, queryset):
        for obj in queryset:
            obj.is_active = False
            obj.save()
        self.message_user(
            request, f"{queryset.count()} models will be switched.")

    disable_models.short_description = "Disable models"

    def enable_models(self, request, queryset):
        for obj in queryset:
            obj.is_active = True
            obj.save()
        self.message_user(
            request, f"{queryset.count()} models will be switched.")

    enable_models.short_description = "Enable models"


@admin.register(MediaIncident)
class MediaIncidentAdmin(admin.ModelAdmin):
    list_display = ("any_title", "incident_type", "status", "rate_article")
    search_fields = ["title"]

    def rate_article(self, obj):
        if obj.related_article:
            return obj.related_article.rate

    rate_article.short_description = "Article rate"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "url",
        "publication_date",
        "is_downloaded",
        "is_parsed",
        "is_duplicate",
        "title",
        "rate",
    )
    ordering = ("-publication_date",)
    actions = ["force_parse"]
    search_fields = ['url', 'title']

    def force_parse(self, request, queryset):
        for obj in queryset:
            obj.is_parsed = False
            obj.save()
        self.message_user(
            request, f"{queryset.count()} articles will be parsed.")

    force_parse.short_description = "Force parse"


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("url", "country", "region", "is_active")
    actions = ["activate", "deactivate"]
    search_fields = ['url']

    def save_model(self, request, obj, form, change):
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

    def activate(self, request, queryset):
        for obj in queryset:
            obj.is_active = True
            obj.save()
        self.message_user(
            request, f"{queryset.count()} sources were deactivate.")

    def deactivate(self, request, queryset):
        for obj in queryset:
            obj.is_active = False
            obj.save()
        self.message_user(
            request, f"{queryset.count()} sources were deactivate.")

    activate.short_description = "Activate sources"
    deactivate.short_description = "Deactivate sources"
