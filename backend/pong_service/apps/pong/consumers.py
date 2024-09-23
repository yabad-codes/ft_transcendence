import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async

logger = logging.getLogger('daphne')


def get_redis_client():
    from django.conf import settings
    return settings.REDIS


class MatchMakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player = self.scope['user']
        await self.accept()
        await self.add_to_queue(str(self.player.id))

    async def disconnect(self, code):
        await self.remove_from_queue(str(self.player.id))

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'cancel_matchmaking':
            await self.remove_from_queue(str(self.player.id))
            await self.send(text_data=json.dumps({
                'status': 'cancelled',
                'message': 'Matchmaking cancelled'
            }))

    @sync_to_async
    def add_to_queue(self, player_id):
        redis_client = get_redis_client()
        redis_client.rpush('game_queue', player_id)
        self.match_players()

    @sync_to_async
    def remove_from_queue(self, player_id):
        redis_client = get_redis_client()
        redis_client.lrem('game_queue', 0, player_id)

    @sync_to_async
    def match_players(self):
        redis_client = get_redis_client()
        if redis_client.llen('game_queue') >= 2:
            player1_id = redis_client.lpop('game_queue').decode('utf-8')
            player2_id = redis_client.lpop('game_queue').decode('utf-8')
            game_id = self.create_game(player1_id, player2_id)
            self.notify_players(player1_id, player2_id, str(game_id))

    @database_sync_to_async
    def create_game(self, player1_id, player2_id):
        from pong_service.apps.pong.models import PongGame
        game = PongGame.objects.create(
            player1_id=player1_id,
            player2_id=player2_id,
            status=PongGame.Status.PENDING
        )
        return game.id

    @sync_to_async
    def notify_players(self, player1_id, player2_id, game_id):
        channel_layer = self.channel_layer
        for player_id in [player1_id, player2_id]:
            async_to_sync(channel_layer.group_send)(
                f'matchmaking_{player_id}',
                {
                    'type': 'game_matched',
                    'game_id': game_id
                }
            )

    async def game_matched(self, event):
        await self.send(text_data=json.dumps({
            'status': 'matched',
            'game_id': event['game_id']
        }))


class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps(
                        {'message': 'Connected to Pong Websocket'}
                        ))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send(text_data=json.dumps({
                        'message': f'yabadwashere : {message}'
                        }))
