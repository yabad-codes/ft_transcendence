from rest_framework.generics import ListCreateAPIView, ListAPIView
from .serializers import *
from .models import Player
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated


class LogoutView(APIView):
    """
    Logout a player.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """
    Login a player.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'user_id': user.id,
                'username': user.username,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(ListCreateAPIView):
    """
    Register a new player.
    """

    queryset = Player.objects.all()
    serializer_class = PlayerRegistrationSerializer
    permission_classes = (AllowAny,)


class PlayerListView(ListAPIView):
    """
    Retrieve a list of all players.
    """

    queryset = Player.objects.all()
    serializer_class = PlayerListSerializer
    permission_classes = [IsAuthenticated]


class PlayerPublicProfileView(generics.RetrieveAPIView):

    """
    Retrieve a player's public profile.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerPublicProfileSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated]
