# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/

import logging

from server.settings import ENV

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s [%(process)d] [%(levelname)s] "
                + "pathname=%(pathname)s lineno=%(lineno)s "
                + "funcname=%(funcName)s %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "console-verbose": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO",
        },
        "parser": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO",
        },
        "security": {
            "handlers": ["console-verbose"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

if ENV == "development":
    LOGGING["loggers"]["parser"]["level"] = "DEBUG"
    LOGGING["loggers"]["security"]["level"] = "DEBUG"
    logging.info("Logging level for parser and security sets to DEBUG")
