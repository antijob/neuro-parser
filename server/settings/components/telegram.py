# -*- coding: utf-8 -*-

"""
Telegram bot configuration module
"""

from server.settings.components import secret

TELEGRAM_BOT_TOKEN = secret("telegram.bot.token")
