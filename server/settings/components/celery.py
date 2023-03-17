# -*- coding: utf-8 -*-

"""
Celery module
"""

from decouple import config as c


CELERY_BROKER_URL = 'redis://{host}:6379/0'.format(host=c('REDIS_HOST'))
