from rest_framework.generics import ListCreateAPIView
from .serializers import  *
from .models import Player
from rest_framework.permissions import AllowAny


class RegisterView(ListCreateAPIView):

    #API view for registering a new player.

    #Inherits from ListCreateAPIView POST requests.
    #POST request creates a new player using the PlayerRegistrationSerializer.

    #Attributes:
        #queryset (QuerySet): The queryset of all players.
        #serializer_class (Serializer): The serializer class for player registration.
        #permission_classes (tuple): The permission classes for the view.

    queryset = Player.objects.all()
    serializer_class = PlayerRegistrationSerializer
    permission_classes = (AllowAny,)