import logging

from asgiref.sync import async_to_sync
from django.contrib import admin, messages
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from server.apps.bot.bot_instance import get_bot
from server.apps.bot.models import (
    Channel,
    ChannelCountry,
    ChannelIncidentType,
)

from .forms import BroadcastForm, ChannelCountryForm

logger = logging.getLogger(__name__)


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

    def broadcast_message(self, request, queryset):
        if "apply" in request.POST:

            form = BroadcastForm(request.POST)

            if "channels" not in request.POST:
                self.message_user(request, "Каналы не выбраны", level=messages.WARNING)
                return None

            if form.is_valid():
                message = form.cleaned_data["message"]
                channels = form.cleaned_data["channels"]

                async def send_messages():
                    success_count = 0
                    async with get_bot() as bot:
                        for channel in channels:
                            try:
                                await bot.send_message(
                                    text=message, chat_id=str(channel)
                                )
                                success_count += 1
                            except Exception as e:
                                logger.error(
                                    f"Failed to send message to channel {channel}: {e}"
                                )
                                continue

                    return success_count

                success_count = async_to_sync(send_messages)()
                self.message_user(
                    request,
                    f"Сообщение отправлено в {success_count} каналов из {len(channels)}",
                    level=messages.INFO,
                )
                return None
        else:
            selected_channels = queryset.values_list("id", flat=True)
            form = BroadcastForm(selected_channels=selected_channels)

            return render(
                request,
                "admin/broadcast_message.html",
                context={
                    "form": form,
                    "channels": queryset,
                },
            )

    broadcast_message.short_description = "Отправить сообщение в выбранные каналы"
    actions = ["broadcast_message"]


@admin.register(ChannelIncidentType)
class ChannelIncidentTypeAdmin(admin.ModelAdmin):
    list_display = ["channel", "incident_type", "status", "show"]
    list_filter = ["channel", "incident_type", "status", "show"]
    inlines = [ChannelSubscriptionInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "show":
            field.help_text = _(
                "При отключении этого поля, поле <b>status</b> также будет отключено"
            )
        return field

    def save_model(self, request, obj, form, change):
        if not obj.show:
            obj.status = False
        super().save_model(request, obj, form, change)


@admin.register(ChannelCountry)
class ChannelSubscriptionAdmin(admin.ModelAdmin):
    form = ChannelCountryForm
    list_display = ["channel_incident_type", "country", "enabled_regions", "status"]
    list_filter = ["channel_incident_type", "country", "status"]
