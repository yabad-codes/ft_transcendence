from django.urls import re_path
from pong_service.apps.pong.match_making_consumer import MatchMakingConsumer
from pong_service.apps.pong.game_consumer import PongConsumer

websocket_urlpatterns = [
    # pong game with game_id in url
	re_path(r'ws/pong/(?P<game_id>\w+)/$', PongConsumer.as_asgi()),
	re_path(r'ws/matchmaking/$', MatchMakingConsumer.as_asgi()),
]