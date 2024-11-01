"""
ASGI config for pong_service project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pong_service.apps.chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from pong_service.apps.pong.routing import websocket_urlpatterns as pong_websocket_urlpatterns

application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	"websocket": AuthMiddlewareStack(
		URLRouter(
			chat_websocket_urlpatterns + pong_websocket_urlpatterns
		)
	),
})

