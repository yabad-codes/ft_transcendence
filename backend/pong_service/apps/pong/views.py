from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from .models import PongGame
from django.conf import settings

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RequestGameView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        player = request.user

        # check if player is already in a game
        active_game = PongGame.objects.filter(
            Q(player1=player) | Q(player2=player),
            status__in=[PongGame.Status.PENDING, PongGame.Status.STARTED]
        ).first()

        if active_game:
            return Response({
                'status': 'error',
                'message': 'You already in game',
                'game_id': str(active_game.id)
            }, status=status.HTTP_400_BAD_REQUEST)

        # check if player is already in queue
        redis_client = settings.REDIS
        queue = redis_client.lrange('game_queue', 0, -1)
        if str(player.id).encode('utf-8') in queue:
            return Response({
                'status': 'error',
                'message': 'You are already in the matchmaking queue',
                'websocket_url': '/ws/matchmaking/'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'status': 'success',
            'message': 'Please connect to the matchmaking websocket',
            'websocket_url': '/ws/matchmaking/'
        }, status=status.HTTP_200_OK)
