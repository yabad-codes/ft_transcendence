from rest_framework.generics import ListCreateAPIView, ListAPIView
from .serializers import *
from .models import Player
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout


class LogoutView(APIView):
    """
    View for logging out a user.

    Requires the user to be authenticated.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Handle POST request to log out the user.

        :param request: The HTTP request object.
        :return: A Response object with a success message.
        """
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """
    View for handling user login.
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
    View for registering a new player.

    Inherits from ListCreateAPIView, which provides GET (list) and POST (create) methods.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerRegistrationSerializer
    permission_classes = (AllowAny,)


class PlayerListView(ListAPIView):
    """
    API view that returns a list of all players.

    Inherits from ListAPIView and uses PlayerListSerializer
    to serialize the queryset.

    Requires authentication for access.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerListSerializer
    permission_classes = [IsAuthenticated]


class PlayerPublicProfileView(generics.RetrieveAPIView):
    """
    API view to retrieve the public profile of a player.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerListSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated]
    
class UpdatePlayerInfoView(generics.UpdateAPIView):
    """
    API view for updating player information.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    serializer_class =  UpdatePlayerInfoSerializer
    
    def get_object(self):
        """
        Get the player object of the currently authenticated user.
        Returns:
        - Player: The player object. 
        """
        return self.request.user

    def patch(self, request):
        """
        Handle PATCH request to update player information.

        Parameters:
        - request: The HTTP request object.

        Returns:
        - Response: The HTTP response object.
        """
        player = request.user
        serializer = self.serializer_class(player, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    queryset = Player.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class =  ChangePasswordSerializer
    
    def get_object(self):
        """
        Get the player object of the currently authenticated user.
        Returns:
        - Player: The player object. 
        """
        return self.request.user
    def put(self, request):
        player=request.user
        serializer=self.serializer_class(player, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
    