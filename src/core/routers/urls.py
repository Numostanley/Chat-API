from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path  # noqa
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

from .versioning import get_api_version
from apis.base import views as base_views
from apis.authentication import views as authentication_views


public_urls: list = [
    path("admin/", admin.site.urls),
    path('auth/', include('apis.authentication.urls', namespace='authentication')),
    path('o/oauth/token', authentication_views.TokenAPIView.as_view(), name='oauth-token'),
    path('o/oauth/refresh', authentication_views.RefreshTokenAPIView.as_view(), name='oauth-refresh-token'),
    path('users/', include('apis.users.urls', namespace='users')),
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('swagger', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    re_path(r'^.*$', base_views.NotFoundAPIView.as_view())
]

api_version: str = get_api_version(settings.API_VERSIONS, 'v1')

if settings.API_PREFIX:
    public_urls: list = [
        path(f'{api_version}/', include(public_urls))
    ]

urlpatterns: list = public_urls
