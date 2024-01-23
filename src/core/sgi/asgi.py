"""
ASGI config for nafe project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from ..settings import get_settings_environment


os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_settings_environment())

application = get_asgi_application()
