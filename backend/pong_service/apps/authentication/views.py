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

    def post(self, request):
        """
        Handle PATCH request to update player information.

        Parameters:
        - request: The HTTP request object.

        Returns:
        - Response: The HTTP response object.
        """
        player = self.get_object()
        serializer = self.serializer_class(player, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"update info successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateAvatarView(generics.UpdateAPIView):
    """
    A view for updating the avatar of the player.
    """
    queryset = Player.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class =  UpdateAvatarSerializers
    
    def get_object(self):
        """
        Get the player object of the currently authenticated user.

        Returns:
        - Player: The player object. 
        """
        return self.request.user
    
    def post(self, request):
        """
        Handle the POST request to update the avatar of the player.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """
        player = self.get_object()
        serializers = UpdateAvatarSerializers(player, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":"update avatar successfully"}, status=status.HTTP_200_OK)
        return Response({"message":"update avatar failure"}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    """
    A view for changing the password of the authenticated player.
    """
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
    
    def post(self, request):
            """
            Handle the POST request to change the password of the authenticated player.

            Args:
                request (HttpRequest): The HTTP request object.

            Returns:
                Response: The HTTP response object containing the result of the password change operation.
            """
            self.object = self.get_object()
            if self.object.password is None:
                serializer = CreatePasswordSerializer(self.object, data=request.data, parial=True,context={'request': request})
            else:    
                serializer= ChangePasswordSerializer(self.object, data=request.data, partial=True, context={'request': request}) 
            
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Password changed successfully"},status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            