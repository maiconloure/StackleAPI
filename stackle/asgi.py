"""
ASGI config for stackle project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from chat.channels_app.routing import application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat.settings")

application = application()