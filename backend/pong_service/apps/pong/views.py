from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from .models import PongGame, GameRequest
from pong_service.apps.authentication.models import Player
from django.shortcuts import get_object_or_404
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

class RequestGameWithPlayerView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        player = request.user
        opponent_id = request.data.get('opponent_id')

        if not opponent_id:
            return Response({
                'status': 'error',
                'message': 'Please provide an opponent_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        opponent = get_object_or_404(Player, id=opponent_id)

        # Check if there's already an active game or request
        active_game = PongGame.objects.filter(
            (Q(player1=player) | Q(player2=player)) &
            Q(status__in=[PongGame.Status.PENDING, PongGame.Status.STARTED])
        ).first()

        if active_game:
            return Response({
                'status': 'error',
                'message': 'You are already in a game',
                'game_id': str(active_game.id)
            }, status=status.HTTP_400_BAD_REQUEST)

        active_request = GameRequest.objects.filter(
            (Q(requester=player) | Q(opponent=player)) &
            Q(status=GameRequest.Status.PENDING)
        ).first()

        if active_request:
            return Response({
                'status': 'error',
                'message': 'You already have a pending game request',
                'request_id': str(active_request.id)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create a new game request
        game_request = GameRequest.objects.create(
            requester=player,
            opponent=opponent,
            status=GameRequest.Status.PENDING
        )

        return Response({
            'status': 'success',
            'message': 'Game request sent',
            'request_id': str(game_request.id)
        }, status=status.HTTP_201_CREATED)

class AcceptGameRequestView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        player = request.user
        request_id = request.data.get('request_id')

        if not request_id:
            return Response({
                'status': 'error',
                'message': 'Please provide a request_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        game_request = get_object_or_404(GameRequest, id=request_id, opponent=player, status=GameRequest.Status.PENDING)

        # Create a new game
        game = PongGame.objects.create(
            player1=game_request.requester,
            player2=game_request.opponent,
            status=PongGame.Status.PENDING
        )

        # Update the game request status
        game_request.status = GameRequest.Status.ACCEPTED
        game_request.save()

        return Response({
            'status': 'success',
            'message': 'Game request accepted',
            'game_id': str(game.id)
        }, status=status.HTTP_200_OK)