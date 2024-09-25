import json
import struct
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from pong_service.apps.pong.binproto import BinaryProtocol
from pong_service.apps.pong.game_logic import PongGame, GAME_WIDTH, GAME_HEIGHT
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from jwt import decode as jwt_decode


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
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'game_start',
                    'game_id': self.game_id
                }
            )
            await self.start()

    async def start(self):
        game = await self.get_or_create_game()
        player1 = await self.get_player(game.player1_id)
        player2 = await self.get_player(game.player2_id)
        self.game = PongGame(player1, player2)
        self.game_loop_task = asyncio.create_task(self.game_loop())

    async def game_loop(self):
        try:
            while True:
                current_time = asyncio.get_event_loop().time()
                game_over = self.game.update(current_time)
                await self.send_game_state()
                if game_over:
                    await asyncio.sleep(3)
                    self.game.ball.reset()
                await asyncio.sleep(1/30)
        except asyncio.CancelledError:
            pass

    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'status': 'game_start',
            'game_id': event['game_id']
        }))

    @database_sync_to_async
    def get_game_ready_status(self):
        from pong_service.apps.pong.models import PongGame
        game = PongGame.objects.get(id=self.game_id)
        return bool(game.player1_id and game.player2)

    @database_sync_to_async
    def get_or_create_game(self):
        from pong_service.apps.pong.models import PongGame
        game, created = PongGame.objects.get_or_create(id=self.game_id)
        if created:
            game.player1 = self.player
        elif not game.player2 and game.player1 != self.player:
            game.player2 = self.player
        game.save()
        return game

    @database_sync_to_async
    def get_player(self, player_id):
        from pong_service.apps.authentication.models import Player
        return Player.objects.get(id=player_id)

    async def send_game_state(self):
        state = self.game.get_state()
        game_state = BinaryProtocol.encode_game_state(
            state['ball_x'],
            state['ball_y'],
            state['paddle1_y'],
            state['paddle2_y'],
            state['score1'],
            state['score2']
        )
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
            self.game.paddle1.y = paddle_y
        else:
            self.game.paddle2.y = paddle_y