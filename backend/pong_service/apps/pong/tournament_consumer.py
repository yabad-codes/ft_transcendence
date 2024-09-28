import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from pong_service.apps.pong.game_logic import PongGame
from pong_service.apps.pong.binproto import BinaryProtocol
from jwt import decode as jwt_decode


class PongTournamentConsumer(AsyncWebsocketConsumer):
    tournament_max_participants = 4
    player_channels = {}
    participants_data = {}
    tournament_data = {
        "first_round": [],
        "second_round": []
    }
    games = {}
    game_loops = {}

    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_name = f'pong_tournament_{self.game_id}'
        self.player = await self.get_user_from_access_token(self.scope['cookies'].get('access'))

        if not self.player:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await self.join_tournament()

    async def disconnect(self, close_code):
        if self.player:
            await self.leave_tournament()
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'paddle_move':
            await self.handle_paddle_move(data['direction'])

    async def join_tournament(self):
        self.participants_data[self.player.id] = "waiting"
        self.player_channels[self.player.id] = self.channel_name

        await self.add_player_to_tournament()
        await self.broadcast_tournament_status()

        if len(self.participants_data) == self.tournament_max_participants:
            await self.start_tournament()

    async def leave_tournament(self):
        if self.player.id in self.participants_data:
            del self.participants_data[self.player.id]
        if self.player.id in self.player_channels:
            del self.player_channels[self.player.id]
        await self.remove_player_from_tournament()
        await self.broadcast_tournament_status()

    async def start_tournament(self):
        tournament = await self.start_tournament_db()
        players = list(self.participants_data.keys())
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                await self.create_match(players[i], players[i+1], tournament)
        self.tournament_max_participants //= 2
        await self.broadcast_tournament_status()

    async def create_match(self, player1_id, player2_id, tournament):
        player1 = await self.get_player_by_id(player1_id)
        player2 = await self.get_player_by_id(player2_id)
        game_model = await self.create_pong_game_model(player1, player2, tournament)
        game = PongGame(player1, player2)
        self.games[game_model.id] = game
        self.game_loops[game_model.id] = asyncio.create_task(
            self.game_loop(game_model.id))
        await self.notify_match_started(player1_id, player2_id, game_model.id)

    async def game_loop(self, game_id):
        game = self.games[game_id]
        try:
            while True:
                game_over = game.update(asyncio.get_event_loop().time())
                await self.send_game_state(game_id)
                if game_over:
                    winner = game.get_winner()
                    await self.end_match(game_id, winner.id)
                    break
                await asyncio.sleep(1/60)
        except asyncio.CancelledError:
            pass

    async def handle_paddle_move(self, direction):
        for game_id, game in self.games.items():
            if self.player.id in [game.player1.id, game.player2.id]:
                game.move_paddle(self.player.id, direction)

    async def send_game_state(self, game_id):
        game = self.games[game_id]
        state = game.get_state()
        game_state = BinaryProtocol.encode_game_state(
            state['ball_x'], state['ball_y'],
            state['paddle1_y'], state['paddle2_y'],
            state['score1'], state['score2']
        )
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'binary_game_state',
                'game_state': game_state,
                'game_id': game_id
            }
        )

    async def binary_game_state(self, event):
        if event['game_id'] in self.games:
            await self.send(bytes_data=event['game_state'])

    async def end_match(self, game_id, winner_id):
        del self.games[game_id]
        self.game_loops[game_id].cancel()
        del self.game_loops[game_id]
        await self.update_tournament_data(winner_id)
        if self.tournament_max_participants == 1:
            await self.end_tournament(winner_id)
        else:
            await self.start_next_round()

    async def start_next_round(self):
        winners = [
            player for player in self.tournament_data['first_round'] if player['win']]
        if len(winners) == self.tournament_max_participants:
            self.tournament_data['second_round'] = winners
            self.tournament_data['first_round'] = []
            for i in range(0, len(winners), 2):
                if i + 1 < len(winners):
                    await self.create_match(winners[i]['id'], winners[i+1]['id'])
            self.tournament_max_participants //= 2

    async def end_tournament(self, winner_id):
        winner = await self.get_player_by_id(winner_id)
        await self.end_tournament_db(winner)
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'tournament_end',
                'winner': winner.username
            }
        )
        # Clean up
        self.participants_data.clear()
        self.tournament_data['first_round'].clear()
        self.tournament_data['second_round'].clear()
        self.player_channels.clear()

    async def tournament_end(self, event):
        await self.send(text_data=json.dumps({
            'type': 'tournament_end',
            'winner': event['winner']
        }))

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

    @database_sync_to_async
    def get_player_by_id(self, player_id):
        from pong_service.apps.authentication.models import Player
        return Player.objects.get(id=player_id)

    @database_sync_to_async
    def create_pong_game_model(self, player1, player2, tournament):
        from pong_service.apps.pong.models import PongGame as PongGameModel
        game = PongGameModel.objects.create(
            player1=player1, player2=player2, status=PongGameModel.Status.STARTED)
        tournament.games.add(game)
        return game

    @database_sync_to_async
    def add_player_to_tournament(self):
        from pong_service.apps.pong.models import Tournament
        tournament, created = Tournament.objects.get_or_create(
            status=Tournament.Status.PENDING)
        tournament.participants.add(self.player)
        return tournament

    @database_sync_to_async
    def remove_player_from_tournament(self):
        from pong_service.apps.pong.models import Tournament
        tournament = Tournament.objects.filter(
            status=Tournament.Status.PENDING).first()
        if tournament:
            tournament.participants.remove(self.player)
            if tournament.participants.count() == 0:
                tournament.delete()

    @database_sync_to_async
    def start_tournament_db(self):
        from pong_service.apps.pong.models import Tournament
        tournament = Tournament.objects.filter(
            status=Tournament.Status.PENDING).first()
        if tournament:
            tournament.status = Tournament.Status.IN_PROGRESS
            tournament.save()
        return tournament

    @database_sync_to_async
    def end_tournament_db(self, winner):
        from pong_service.apps.pong.models import Tournament
        tournament = Tournament.objects.filter(
            status=Tournament.Status.IN_PROGRESS).first()
        if tournament:
            tournament.status = Tournament.Status.FINISHED
            tournament.winner = winner
            tournament.save()

    async def broadcast_tournament_status(self):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'tournament_status',
                'participants': list(self.participants_data.keys()),
                'tournament_data': self.tournament_data
            }
        )

    async def tournament_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'tournament_status',
            'participants': event['participants'],
            'tournament_data': event['tournament_data']
        }))

    async def notify_match_started(self, player1_id, player2_id, game_id):
        for player_id in [player1_id, player2_id]:
            await self.channel_layer.send(
                self.player_channels[player_id],
                {
                    'type': 'match_started',
                    'game_id': game_id,
                    'opponent_id': player1_id if player_id == player2_id else player2_id
                }
            )

    async def match_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'match_started',
            'game_id': event['game_id'],
            'opponent_id': event['opponent_id']
        }))

    async def update_tournament_data(self, winner_id):
        for round_data in [self.tournament_data['first_round'], self.tournament_data['second_round']]:
            for player in round_data:
                if player['id'] == winner_id:
                    player['win'] = True
        await self.broadcast_tournament_status()
