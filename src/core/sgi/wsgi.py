"""
WSGI config for chatapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from ..settings import get_settings_environment


os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_settings_environment())

application = get_wsgi_application()
