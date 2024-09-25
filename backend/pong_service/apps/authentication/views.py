from rest_framework.generics import CreateAPIView, ListAPIView
from .serializers import *
from .models import Player
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from pong_service.permissions import IsUnauthenticated
from pong_service.apps.chat.models import BlockedUsers
from django.db.models import Q
from django.http import Http404
from .helpers import set_cookie

from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView
)
from django.conf import settings

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining a new access and refresh token pair.
    
    Args:
		TokenObtainPairView: The default view for obtaining a new access and refresh token pair.
	
	Returns:
		Response: A response object with the new access and refresh tokens.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to obtain a new access and refresh token pair.
		1. Call the parent class's post method to obtain the tokens.
		2. If the response status code is 200, set the tokens in cookies.
        """
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response = set_cookie(
                response,
                'access',
                response.data['access'],
                settings.AUTH_COOKIE_ACCESS_MAX_AGE
            )
            response = set_cookie(
                response,
            	'refresh',
            	response.data['refresh'],
            	settings.AUTH_COOKIE_REFRESH_MAX_AGE
            )
        return response

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for refreshing an access token.
    
    Args:
		TokenRefreshView: The default view for refreshing an access token.
	
	Returns:
		Response: A response object with the new access token.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to refresh the access token.
        1. Get the refresh token from the request cookies.
        2. If the refresh token is present, add it to the request data.
        3. Call the parent class's post method to refresh the access token.
        4. If the response status code is 200, set the new access token in a cookie.
        """
        refresh = request.COOKIES.get('refresh')
        if refresh:
            data = request.data.copy()
            data['refresh'] = refresh
            request._full_data = data
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response = set_cookie(
                response,
                'access',
                response.data['access'],
                settings.AUTH_COOKIE_ACCESS_MAX_AGE
            )
        return response

class LogoutView(APIView):
    """
    View for logging out a user.

    Requires the user to be authenticated.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
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
    permission_classes = (IsUnauthenticated,)
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

class RegisterView(CreateAPIView):
    """
    View for registering a new player.

    Inherits from CreateAPIView, which provides POST (create) method.
    """
    permission_classes = (IsUnauthenticated,)
    serializer_class = PlayerRegistrationSerializer
    queryset = Player.objects.all()
    
    def post(self, request):
        """
        Handle POST request to register a new player.

        :param request: The HTTP request object.
        :return: A Response object with a success message.
        """
        
        serializer = PlayerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registration successful'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def get_queryset(self):
        """
        Exclude blocked users from the queryset.
        """
        blocked_users = BlockedUsers.objects.filter(
            Q(player=self.request.user) | Q(blockedUser=self.request.user)
        )
        blocked_user_ids = blocked_users.values_list('blockedUser', flat=True)
        return Player.objects.exclude(id__in=blocked_user_ids)


class PlayerPublicProfileView(generics.RetrieveAPIView):
    """
    API view to retrieve the public profile of a player.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerListSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """
        Exclude blocked users from the queryset.
        """
        username = self.kwargs['username']
        if BlockedUsers.objects.filter(
            Q(player=self.request.user, blockedUser__username=username) |
            Q(player__username=username, blockedUser=self.request.user)
        ).exists():
            raise Http404("Player not found")
        return super().get_object()

class PlayerProfileView(generics.RetrieveAPIView):
    """
    API view to retrieve the profile of the currently authenticated player.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PlayerListSerializer

    def get_object(self):
        """
        Get the player object of the currently authenticated user.
        Returns:
        - Player: The player object. 
        """

        return self.request.user

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

