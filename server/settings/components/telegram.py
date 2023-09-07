# -*- coding: utf-8 -*-

"""
Telegram bot configuration module
"""

from decouple import config as c
c.path='../../../.env'

TELEGRAM_BOT_TOKEN = c('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_NAME = c('TELEGRAM_BOT_NAME')
