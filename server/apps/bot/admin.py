from django.contrib import admin

from server.apps.bot.models import (
    Channel,
    ChannelIncidentType,
    ChannelCountry,
)


class ChannelIncidentTypeInline(admin.TabularInline):
    model = ChannelIncidentType
    extra = 1


class ChannelSubscriptionInline(admin.TabularInline):
    model = ChannelCountry
    extra = 1


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ["channel_id"]
    inlines = [ChannelIncidentTypeInline]


@admin.register(ChannelIncidentType)
class ChannelIncidentTypeAdmin(admin.ModelAdmin):
    list_display = ["channel", "incident_type", "status"]
    inlines = [ChannelSubscriptionInline]


@admin.register(ChannelCountry)
class ChannelSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["channel_incident_type", "country", "enabled_regions", "status"]
    list_filter = ["channel_incident_type", "country", "status"]
