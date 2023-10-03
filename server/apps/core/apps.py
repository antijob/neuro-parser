from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    """Default django-app configuration."""

    name = 'server.apps.core'

    def ready(self):
        import server.apps.core.signals
