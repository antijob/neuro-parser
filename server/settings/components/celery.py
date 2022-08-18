# -*- coding: utf-8 -*-

"""
Celery module
"""

from server.settings.components import env, secret


CELERY_BROKER_URL = 'redis://{host}:6379/0'.format(host=env('REDIS_HOST'))
