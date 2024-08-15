# -*- coding: utf-8 -*-

"""
REST api settings module
"""


from decouple import config as c

c.path = "../../../.env"

API_TOKEN = c("API_TOKEN", default=None)
API_RPS = c("API_RPS", default="1/second")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "server.apps.api.authentication.EnvTokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "server.apps.api.throttling.StaffUserRateThrottle",
        "server.apps.api.throttling.RegularUserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "staff_user": API_RPS,
        "regular_user": API_RPS,
    },
    "EXCEPTION_HANDLER": "server.apps.api.exception_handler.custom_exception_handler",
}
