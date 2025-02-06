"""
Telethon client configuration module
"""

from decouple import config as c

c.path = "../../../.env"

TELEGRAM_API_ID = c("TELEGRAM_API_ID")
TELEGRAM_API_HASH = c("TELEGRAM_API_HASH")
