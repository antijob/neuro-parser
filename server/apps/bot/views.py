import json
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import (
                            CommandHandler,
                            Filters,
                            MessageHandler,
                            Updater,
                            CallbackQueryHandler,
                        )

from server.apps.bot.logic.handlers import (
    help_callback,
    new_chat_members,
    categ,
)
from server.apps.bot.logic.keyboard import button
from server.settings.components.telegram import TELEGRAM_BOT_TOKEN

updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("help", help_callback))
dispatcher.add_handler(CommandHandler("start", help_callback))
dispatcher.add_handler(CommandHandler("categ", categ))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_members))
dispatcher.add_handler(MessageHandler(Filters.all, help_callback))


@method_decorator(csrf_exempt, name="dispatch")
class TelegramBotWebhookView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            data = json.loads(request.body)
            update = Update.de_json(data, updater.bot)
            dispatcher.process_update(update)
            return JsonResponse({"ok": "POST request processed"}, status=200)
        except:
            return JsonResponse({"error": "Unknown error"}, status=500)
