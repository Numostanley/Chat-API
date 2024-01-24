"""
ASGI config for chatapi project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from ..settings import get_settings_environment
from apis.chat import routing
from apis.chat.tokenauth_middleware import TokenAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_settings_environment())

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddleware(URLRouter(routing.websocket_urlpatterns)))
})
