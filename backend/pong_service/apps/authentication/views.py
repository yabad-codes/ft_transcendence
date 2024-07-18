from rest_framework.generics import ListCreateAPIView , ListAPIView
from .serializers import  *
from .models import Player
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import permissions


#POST request creates a new player using the PlayerRegistrationSerializer.
class RegisterView(ListCreateAPIView):

    queryset = Player.objects.all()
    serializer_class = PlayerRegistrationSerializer
    permission_classes = (AllowAny,)


#GET request lists all players using the PlayerListSerializer.
class PlayerListView(ListAPIView):

    queryset = Player.objects.all()
    serializer_class = PlayerListSerializer
    permission_classes = [permissions.AllowAny]

#GET request retrieves a player's public profile using the PlayerPublicProfileSerializer.
class PlayerPublicProfileView(generics.RetrieveAPIView):

    queryset = Player.objects.all()
    serializer_class = PlayerPublicProfileSerializer
    lookup_field = 'username'
    permission_classes = [permissions.AllowAny]


