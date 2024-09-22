from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from pong_service.apps.authentication.models import Player
from .models import PongGame
from django.db.models import Q
import logging

redis_client = settings.REDIS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class RequestGameView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        player = request.user
        
        active_game = PongGame.objects.filter(
            Q(player1=player) | Q(player2=player),
            status__in=[PongGame.Status.PENDING, PongGame.Status.STARTED]
        ).first()
        
        logger.debug(f'Active game: {active_game}')
        
        # check if player is already in queue
        in_queue = redis_client.lrange('game_queue', 0, -1)
        if in_queue:
            in_queue = [player_id.decode('utf-8') for player_id in in_queue]
            if str(player.id) in in_queue:
                in_queue = True
            else:
                in_queue = False
        
        if active_game or in_queue:
            return Response({
                'status': 'error',
                'message': 'You already have an active game or waiting for an opponent',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        player_id = str(player.id)
        redis_client.rpush('game_queue', player_id)
        
        if redis_client.llen('game_queue') >= 2:
            player1_id = redis_client.lpop('game_queue').decode('utf-8')
            player2_id = redis_client.lpop('game_queue').decode('utf-8')
            
            game_id = self.create_game(player1_id, player2_id)
            
            return Response({
                'status': 'success',
                'message': 'Game created',
                'game_id': game_id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'success',
                'message': 'Waiting for an opponent'
            }, status=status.HTTP_202_ACCEPTED)
    
    def create_game(self, player1_id, player2_id):
        player1 = Player.objects.get(id=player1_id)
        player2 = Player.objects.get(id=player2_id)
        game = PongGame.objects.create(player1=player1, player2=player2, status=PongGame.Status.PENDING)
        return game.id