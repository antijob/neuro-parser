# -*- coding: utf-8 -*-

"""
Sentry configuration module
"""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from decouple import config as c

c.path = '../../../.env'
SENTRY_DSN = c('SENTRY_DSN')


def before_send(event, hint):
    if event.get('level') == 'warning':
        return None
    return event


sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    send_default_pii=True,
    before_send=before_send,
    sample_rate=0.1,  # 10% of errors events
    traces_sample_rate=0.01,  # 1% of events of tracing
)
