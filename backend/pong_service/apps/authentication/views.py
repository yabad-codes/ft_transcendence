from rest_framework.generics import ListCreateAPIView, ListAPIView
from .serializers import *
from .models import Player
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.conf import settings
import logging
import requests
from django.shortcuts import redirect

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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


class OAuthLoginView(APIView):
    def get(self, request):
        logger.debug('Redirecting to OAuth login page')
        return redirect(settings.AUTH_URL)


class OAuthCallbackView(APIView):
    def get(self, request):
        logger.debug('Received OAuth callback')
        if 'code' in request.GET:
            code = request.GET['code']
            token_url = settings.TOKEN_URL
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': settings.UID,
                'client_secret': settings.SECRET,
                'redirect_uri': settings.REDIRECT_URL
            }
            token_response = requests.post(token_url, data=token_data)
            token_response_data = token_response.json()
            logger.debug(f'Token response: {token_response_data}') 
            access_token = token_response_data.get('access_token')
            if access_token:
                logger.debug(f'Access token: {access_token}')
                # get user data
                api_url = settings.API_URL
                headers = {
                    'Authorization': f'Bearer {access_token}'
                }
                user_response = requests.get(api_url, headers=headers)
                user_response_data = user_response.json()
                logger.debug(f'User data: {user_response_data}')
        return redirect('https://google.com')


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
