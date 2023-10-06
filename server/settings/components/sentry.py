# -*- coding: utf-8 -*-

"""
Sentry configuration module
"""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from decouple import config as c

c.path='../../../.env'
SENTRY_DSN = c('SENTRY_DSN')

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        DjangoIntegration(),
    ],
    send_default_pii=True,
)
