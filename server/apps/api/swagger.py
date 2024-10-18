from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import include, path


from server.apps.api import urls as api_urls


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Documentation for neuro parser",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="info@antijob.net"),
        license=openapi.License(
            name="Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)",
            url="https://creativecommons.org/licenses/by-nc/4.0/"
        ),
    ),
    # url=f'{settings.APP_URL}/api/v3/',
    patterns=[
        path("api/", include(api_urls, namespace="api")),
    ],
    public=True,
    permission_classes=(permissions.AllowAny,),
)
