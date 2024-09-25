import json
import struct
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async
from jwt import decode as jwt_decode

active_connections = {}

# Constants for the game
PADDLE_HEIGHT = 120
PADDLE_WIDTH = 12
BALL_SIZE = 20
GAME_WIDTH = 1400
GAME_HEIGHT = 700


def get_redis_client():
    from django.conf import settings
    return settings.REDIS


class BinaryProtocol:
    @staticmethod
    def encode_game_state(ball_x, ball_y, pad1_y, pad2_y, score1, score2):
        return struct.pack('!ffffII', ball_x, ball_y, pad1_y, pad2_y, score1, score2)

    @staticmethod
    def decode_game_state(data):
        return struct.unpack('!ffffII', data)


class MatchMakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.conf import settings
        self.cookies = self.scope['cookies']
        self.access = self.cookies.get(settings.AUTH_COOKIE)

        if self.access:
            self.player = await self.get_user_from_access_token(self.access)
            print(f'Player {
                  self.player.username} connected to matchmaking from yabad was here!!!')
        else:
            self.player = None

        if not self.player or not self.player.is_authenticated:
            print('Player not authenticated')
            await self.close()
        else:
            print(f'Player {self.player.username} connected to matchmaking')
            active_connections[str(self.player.id)] = self
            await self.accept()
            await self.add_to_queue(str(self.player.id))

    async def get_user_from_access_token(self, access_token):
        from django.conf import settings
        from pong_service.apps.authentication.models import Player
        from jwt import InvalidTokenError
        from rest_framework_simplejwt.exceptions import TokenError
        try:
            decoded_token = await sync_to_async(jwt_decode)(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get('user_id')

            if user_id is None:
                return None

            user = await sync_to_async(Player.objects.get)(id=user_id)
            return user
        except (TokenError, InvalidTokenError, Player.DoesNotExist):
            return None

    async def disconnect(self, code):
        if hasattr(self, 'player') and self.player:
            active_connections.pop(str(self.player.id), None)
            await self.remove_from_queue(str(self.player.id))

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'cancel_matchmaking':
            await self.remove_from_queue(str(self.player.id))
            await self.send(text_data=json.dumps({
                'status': 'cancelled',
                'message': 'Matchmaking cancelled'
            }))

    @database_sync_to_async
    def get_player(self, username):
        from pong_service.apps.authentication.models import Player
        try:
            return Player.objects.get(username=username)
        except Player.DoesNotExist:
            return None

    async def add_to_queue(self, player_id):
        await self.add_to_redis_queue(player_id)
        await self.match_players()

    @sync_to_async
    def add_to_redis_queue(self, player_id):
        redis_client = get_redis_client()
        redis_client.rpush('game_queue', player_id)

    @sync_to_async
    def remove_from_queue(self, player_id):
        redis_client = get_redis_client()
        redis_client.lrem('game_queue', 0, player_id)

    async def match_players(self):
        queue_length = await self.get_queue_length()
        if queue_length >= 2:
            player1_id, player2_id = await self.get_players_from_queue()
            game_id = await self.create_game(player1_id, player2_id)
            await self.notify_players(player1_id, player2_id, str(game_id))

    @sync_to_async
    def get_queue_length(self):
        redis_client = get_redis_client()
        return redis_client.llen('game_queue')

    @sync_to_async
    def get_players_from_queue(self):
        redis_client = get_redis_client()
        player1_id = redis_client.lpop('game_queue').decode('utf-8')
        player2_id = redis_client.lpop('game_queue').decode('utf-8')
        return player1_id, player2_id

    @database_sync_to_async
    def create_game(self, player1_id, player2_id):
        from pong_service.apps.pong.models import PongGame
        game = PongGame.objects.create(
            player1_id=player1_id,
            player2_id=player2_id,
            status=PongGame.Status.PENDING
        )
        return game.id

    @database_sync_to_async
    def get_player_connection(self, player_id):
        return active_connections.get(player_id)

    async def notify_players(self, player1_id, player2_id, game_id):
        for player_id in [player1_id, player2_id]:
            connection = await self.get_player_connection(player_id)
            if connection:
                await connection.send(text_data=json.dumps({
                    'status': 'matched',
                    'game_id': str(game_id)
                }))
            else:
                print(f"Warning: No active connection for player {player_id}")


class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.cookies = self.scope['cookies']
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_name = f'pong_{self.game_id}'
        access = self.cookies.get('access')

        if not access:
            self.player = None
        else:
            self.player = await self.get_user_from_access_token(self.cookies.get('access'))

        if not self.player:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        print(f'Player {self.player.username} connected to game {
              self.game_id}')
        await self.accept()

        await self.check_if_game_ready()

    async def disconnect(self, close_code):
        if not self.player:
            return
        print(f'Player {self.player.username} disconnected from game {
              self.game_id}')
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, bytes_data):
        paddle_y = struct.unpack('!f', bytes_data)[0]
        await self.update_paddle_position(paddle_y)

    async def get_user_from_access_token(self, access_token):
        from django.conf import settings
        from pong_service.apps.authentication.models import Player
        from jwt import InvalidTokenError
        from rest_framework_simplejwt.exceptions import TokenError
        try:
            decoded_token = await sync_to_async(jwt_decode)(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get('user_id')

            if user_id is None:
                return None

            user = await sync_to_async(Player.objects.get)(id=user_id)
            return user
        except (TokenError, InvalidTokenError, Player.DoesNotExist):
            return None

    async def check_if_game_ready(self):
        is_ready = await self.get_game_ready_status()
        if is_ready:
            print('Game is ready')
            await self.initialize_game()
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'game_start',
                    'game_id': self.game_id
                }
            )

    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'status': 'game_start',
            'game_id': event['game_id']
        }))

    @database_sync_to_async
    def get_game_ready_status(self):
        from pong_service.apps.pong.models import PongGame
        game = PongGame.objects.get(id=self.game_id)
        return bool(game.player1 and game.player2)

    async def initialize_game(self):
        print('Initializing game')
        self.ball_x = GAME_WIDTH / 2
        self.ball_y = GAME_HEIGHT / 2
        self.paddle1_y = GAME_HEIGHT / 2 - PADDLE_HEIGHT / 2
        self.paddle2_y = GAME_HEIGHT / 2 - PADDLE_HEIGHT / 2
        self.score1 = 0
        self.score2 = 0
        self.ball_dx = random.choice([-1, 1]) * 5
        self.ball_dy = random.choice([-1, 1]) * 5

        await self.send_game_state()
        print('Game initialized and initial game state sent')

    async def send_game_state(self):
        game_state = BinaryProtocol.encode_game_state(
            self.ball_x, self.ball_y, self.paddle1_y, self.paddle2_y, self.score1, self.score2
        )
        print('Sending game state data : ', game_state)
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'binary_game_state',
                'game_state': game_state
            }
        )

    async def binary_game_state(self, event):
        await self.send(bytes_data=event['game_state'])

    async def update_paddle_position(self, paddle_y):
        if self.player == self.game.player1:
            self.paddle1_y = paddle_y
        else:
            self.paddle2_y = paddle_y

        await self.send_game_state()

    @database_sync_to_async
    def update_game_state(self):
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        if self.ball_y <= 0 or self.ball_y >= GAME_HEIGHT - BALL_SIZE:
            self.ball_dy *= -1

        if (0 < self.ball_x < PADDLE_WIDTH and self.paddle1_y < self.ball_y < self.paddle1_y + PADDLE_HEIGHT) or \
           (GAME_WIDTH - PADDLE_WIDTH < self.ball_x < GAME_WIDTH and self.paddle2_y < self.ball_y < self.paddle2_y + PADDLE_HEIGHT):
            self.ball_dx *= -1

        # Score points
        if self.ball_x <= 0:
            self.score2 += 1
            self.reset_ball()
        elif self.ball_x >= GAME_WIDTH:
            self.score1 += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball_x = GAME_WIDTH / 2
        self.ball_y = GAME_HEIGHT / 2
        self.ball_dx = random.choice([-1, 1]) * 5
        self.ball_dy = random.choice([-1, 1]) * 5
