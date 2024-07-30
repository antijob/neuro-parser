# -*- coding: utf-8 -*-

"""
Main URL mapping configuration file.

Include other URL сonfs from external apps using method `include()`.

It is also a good practice to keep a single URL to the root index page.

This examples uses Django's default media
files serving technique in development.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from server.apps.api import urls as api_urls
from server.apps.core import urls as main_urls
from server.apps.users import urls as users_urls
from server.apps.bot import urls as bot_urls


from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view  # new
from drf_yasg import openapi  # new
from django.conf.urls import url


admin.autodiscover()



schema_view = get_schema_view(  # new
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    # url=f'{settings.APP_URL}/api/v3/',
    patterns=[path('api/', include(api_urls, namespace='api')), ],
    public=True,
    # permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('s/ecret/admin/doc/', include('django.contrib.admindocs.urls')),
    path('s/ecret/admin/', admin.site.urls),

    # Text and xml static files:
    path('robots.txt', TemplateView.as_view(
        template_name='txt/robots.txt',
        content_type='text/plain',
    )),
    path('humans.txt', TemplateView.as_view(
        template_name='txt/humans.txt',
        content_type='text/plain',
    )),

    path('s/accounts/', include('allauth.urls')),

    # It is a good practice to have explicit index view:

    # Core URLs:
    path('api/', include(api_urls, namespace='api')),
    path('', include(bot_urls, namespace='bot')),
    path('', include(main_urls, namespace='core')),
    path('users/', include(users_urls, namespace='users')),

    path(  # new
        'swagger-ui/',
        TemplateView.as_view(
            template_name='swaggerui/swaggerui.html',
            extra_context={'schema_url': 'openapi-schema'}
        ),
        name='swagger-ui'),
    url(  # new
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'),
]

# if settings.DEBUG:
#     import debug_toolbar
#     from django.views.static import serve

#     urlpatterns = [
#         # URLs specific only to django-debug-toolbar:
#         path('__debug__/', include(debug_toolbar.urls)),

#         # Serving media files in development only:
#         re_path(r'^uploads/(?P<path>.*)$', serve, {
#             'document_root': settings.MEDIA_ROOT,
#         }),
#     ] + urlpatterns
