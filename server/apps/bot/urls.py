from django.urls import path

from server.apps.bot.views import TelegramBotWebhookView

urlpatterns = [
    path("bot/", TelegramBotWebhookView.as_view(), name="bot_webhook"),
]

app_name = "bot"
