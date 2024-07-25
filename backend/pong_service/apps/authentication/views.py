from rest_framework.generics import ListCreateAPIView , ListAPIView
from .serializers import  *
from .models import Player
from rest_framework.permissions import AllowAny 
from rest_framework import generics

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
   
class PlayerPublicProfileView(generics.RetrieveAPIView):

    """
    Retrieve a player's public profile.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerPublicProfileSerializer
    lookup_field = 'username'