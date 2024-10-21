import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django

django.setup()

app = Celery("server")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = "UTC"
app.autodiscover_tasks(
    [
        "server.celery.crawler",
        "server.celery.parser",
        "server.celery.bot",
    ],
    force=True,
)


app.conf.beat_schedule = {
    "crawl": {
        "task": "crawl_chain",
        "schedule": crontab(minute="*/15", hour="*"),
        "options": {
            "expires": 60 * 15,
        },
    },
    "parse": {
        "task": "parse_chain",
        "schedule": crontab(minute="*/15", hour="*"),
        "options": {
            "expires": 60 * 15,
        },
    },
}
