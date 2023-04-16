# -*- coding: utf-8 -*-
from decouple import config as c

"""
Celery module
"""
c.path='../../../.env'


CELERY_BROKER_URL = 'redis://{host}:6379/0'.format(host=c('REDIS_HOST'))
