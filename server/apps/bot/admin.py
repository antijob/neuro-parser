from django.contrib import admin

from .forms import ChannelCountryForm

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
    list_display = ["channel", "incident_type", "status", "allowed"]
    inlines = [ChannelSubscriptionInline]
    list_filter = ["channel", "incident_type", "allowed"]

    def switch_allowance(self, request, queryset):
        for obj in queryset:
            obj.allowed = not obj.allowed
            obj.save()
        self.message_user(
            request, f"For {queryset.count()} models allowance was switched."
        )

    switch_allowance.short_description = "Изменить доступность категории для канала"

    actions = [switch_allowance]


@admin.register(ChannelCountry)
class ChannelSubscriptionAdmin(admin.ModelAdmin):
    form = ChannelCountryForm
    list_display = ["channel_incident_type", "country", "enabled_regions", "status"]
    list_filter = ["channel_incident_type", "country", "status"]
