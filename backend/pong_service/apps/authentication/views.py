from rest_framework.generics import ListCreateAPIView, ListAPIView
from .serializers import *
from .models import Player
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
import pong_service.apps.authentication.helpers as helpers
import logging
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class OAuthLoginView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        logger.debug('Redirecting to OAuth login page')
        logger.info('AUTH_URL: %s', settings.AUTH_URL)
        return redirect(settings.AUTH_URL)
    
class OAuthCallbackView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        logger.debug('Received OAuth callback')
        
        code = request.GET.get('code')
        if not code:
            return self._response_with_message('No code in request', status.HTTP_400_BAD_REQUEST)
        
        access_token = self._get_access_token(code)
        if not access_token:
            return self._response_with_message('Failed to get access token', status.HTTP_400_BAD_REQUEST)
        
        user_data = helpers.get_42_user_data(access_token)
        if not user_data:
            return self._response_with_message('Failed to get user data', status.HTTP_400_BAD_REQUEST)
        
        user_data = helpers.construct_user_data(user_data)
        try:
            if helpers.user_already_exists(user_data):
                return self._login_user(request, user_data)
            return self._create_user(request, user_data)
        except IntegrityError as e:
            return self._response_with_message('Failed to create user', status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return self._response_with_message('Failed to get user data', status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self._response_with_message('An error occurred', status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _response_with_message(self, message, status_code):
        logger.debug(message)
        return Response({'message': message}, status=status_code)
    
    def _get_access_token(self, code):
        try:
            token_response = helpers.get_42_token(code)
            logger.debug('Access token response: %s', token_response)
            return token_response.get('access_token')
        except Exception as e:
            logger.error(f'Failed to get access token: {e}')
            return None
        
    def _login_user(self, request, user_data):
        user = Player.objects.get(api_user_id=user_data['api_user_id'])
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)
        response = JsonResponse({'status': 'success', 'message': 'Login successful'})
        helpers.set_cookie(response, 'access', access_token, settings.AUTH_COOKIE_ACCESS_MAX_AGE)
        helpers.set_cookie(response, 'refresh', refresh_token, settings.AUTH_COOKIE_REFRESH_MAX_AGE)
        logger.debug('User %s logged in successfully', user.username)
        return response
    
    def _create_user(self, request, user_data):
        player = create_player(user_data)
        logger.debug('User %s created successfully', player.username)
        return self._response_with_message('User created successfully', status.HTTP_201_CREATED)

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
            response = helpers.set_cookie(
                response,
                'access',
                response.data['access'],
                settings.AUTH_COOKIE_ACCESS_MAX_AGE
            )
            response = helpers.set_cookie(
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
            response = helpers.set_cookie(
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
