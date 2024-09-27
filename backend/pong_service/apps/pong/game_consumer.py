import json
import struct
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from pong_service.apps.pong.binproto import BinaryProtocol
from pong_service.apps.pong.game_logic import PongGame
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from jwt import decode as jwt_decode


class PongConsumer(AsyncWebsocketConsumer):
    games = {}
    game_loops = {}

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
        await self.accept()

        await self.check_if_game_ready()

    async def disconnect(self, close_code):
        if not self.player:
            return

        if self.game_id in self.games:
            del self.games[self.game_id]
        if self.game_id in self.game_loops:
            self.game_loops[self.game_id].cancel()
            del self.game_loops[self.game_id]

        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if not self.player:
            return
        if text_data in ['w', 's']:
            await self.update_paddle_position(text_data)

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
        await self.send(text_data=json.dumps({
            'status': 'player-role',
            'role': self.player_role,
            'username': self.player_username
        }))
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

        if self.game_id not in self.games:
            self.games[self.game_id] = PongGame(player1, player2)
        self.game = self.games[self.game_id]

        if self.game_id not in self.game_loops:
            self.game_loops[self.game_id] = asyncio.create_task(
                self.game_loop())

    async def game_loop(self):
        try:
            while True:
                current_time = asyncio.get_event_loop().time()
                game_over = self.game.update(current_time)
                await self.send_game_state()
                if game_over:
                    await self.send_game_over()
                    await asyncio.sleep(3)
                    self.game.reset_ball()
                await asyncio.sleep(1/60)
        except asyncio.CancelledError:
            print("Game loop cancelled")
        finally:
            await self.end_game()

    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'status': 'game_start',
            'game_id': event['game_id']
        }))

    @database_sync_to_async
    def get_game_ready_status(self):
        from pong_service.apps.pong.models import PongGame
        game = PongGame.objects.get(id=self.game_id)
        self.player_role = 'player1' if game.player1 == self.player else 'player2'
        self.player_username = self.player.username
        return bool(game.player1 and game.player2)

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

    async def update_paddle_position(self, key):
        direction = 'up' if key == 'w' else 'down'
        self.game.move_paddle(self.player.id, direction)

    async def send_game_over(self):
        winner = self.game.get_winner()
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'game_over',
                'winner': self.game.player1.username if winner == self.game.player1 else self.game.player2.username
            }
        )

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'status': 'game_over',
            'winner': event['winner']
        }))

    async def end_game(self):
        try:
            # Update the game status in the database
            await self.update_game_status()
        except Exception as e:
            pass

        # Clean up the game instance and loop
        if self.game_id in self.games:
            del self.games[self.game_id]
        if self.game_id in self.game_loops:
            del self.game_loops[self.game_id]
        await self.close()

    @database_sync_to_async
    def update_game_status(self):
        from pong_service.apps.pong.models import PongGame
        from pong_service.apps.authentication.models import Player

        game = PongGame.objects.get(id=self.game_id)
        winner = self.game.get_winner()
        game.status = PongGame.Status.FINISHED
        game.player1_score = self.game.scores[self.game.player1.id]
        game.player2_score = self.game.scores[self.game.player2.id]
        game.winner = winner
        game.save()
