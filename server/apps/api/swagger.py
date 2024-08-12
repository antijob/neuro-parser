from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import include, path


from server.apps.api import urls as api_urls


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    # url=f'{settings.APP_URL}/api/v3/',
    patterns=[
        path("api/", include(api_urls, namespace="api")),
    ],
    public=True,
    # permission_classes=(permissions.AllowAny,),
)
