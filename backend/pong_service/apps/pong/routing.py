from django.urls import re_path
from pong_service.apps.pong.consumers import PongConsumer, MatchMakingConsumer

websocket_urlpatterns = [
	re_path(r'ws/pong/$', PongConsumer.as_asgi()),
	re_path(r'ws/matchmaking/(?P<player_username>[^/]+)/$', MatchMakingConsumer.as_asgi()),
]