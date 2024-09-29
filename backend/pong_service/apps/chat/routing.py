from django.urls import re_path
from pong_service.apps.chat.consumers import ChatConsumer, NotificationConsumer

websocket_urlpatterns = [
	re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
	re_path(r'ws/notification/$', NotificationConsumer.as_asgi()),
]
