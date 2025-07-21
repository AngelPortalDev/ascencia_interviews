"""
ASGI config for ascencia_interviews project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from ascencia_interviews.consumers import AudioStreamConsumer  # adjust if needed
import django
from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ascencia_interviews.settings')

# application = get_asgi_application()

django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r"ws/audio/$", AudioStreamConsumer.as_asgi()),
        ])
    ),
})
