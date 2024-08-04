# Standard library imports
import logging

# Third-party library imports
from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Django imports
from django.conf import settings
from django.contrib.auth import login, logout
from django.db.utils import IntegrityError
from django.shortcuts import redirect

# Local application imports
from .models import Player
from .serializers import LoginSerializer, PlayerRegistrationSerializer, PlayerListSerializer
from .helpers import get_42_tokens, get_42_user_data, construct_user_data, create_player, user_already_exists

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
    """
    View for redirecting to the OAuth login page.
    """

    def get(self, request):
        """
        Handle GET requests for OAuth login.

        This method redirects the user to the OAuth login page.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponseRedirect: A redirect response to the OAuth login page.
        """
        logger.debug('Redirecting to OAuth login page')
        return redirect(settings.AUTH_URL)


class OAuthCallbackView(APIView):
    """
    View for handling OAuth callback from 42 API.
    """

    def get(self, request):
        """
        Handle GET request for OAuth callback.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object.

        Raises:
            IntegrityError: If the user already exists.
            KeyError: If there is an invalid user data.
            Exception: If there is an unexpected error.
        """
        logger.debug('Received OAuth callback')

        code = request.GET.get('code')
        if not code:
            return self._response_with_message('No code in request', status.HTTP_400_BAD_REQUEST)

        access_token = self._get_access_token(code)
        if not access_token:
            return self._response_with_message('Failed to retrieve access token', status.HTTP_400_BAD_REQUEST)

        user_data = get_42_user_data(access_token)
        if not user_data:
            return self._response_with_message('Failed to retrieve user data', status.HTTP_400_BAD_REQUEST)

        user_data = construct_user_data(user_data)
        try:
            if user_already_exists(user_data):
                return self._login_user(request, user_data)
            return self._create_user(request, user_data)

        except IntegrityError:
            return self._response_with_message('User already exists', status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            logger.error('Key error: %s', str(e))
            return self._response_with_message('Invalid user data', status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error('Unexpected error: %s', str(e))
            return self._response_with_message('Internal server error', status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _login_user(self, request, user_data):
        """
        Logs in the user with the provided user data.

        Args:
            request (HttpRequest): The HTTP request object.
            user_data (dict): The user data containing the 'api_user_id'.

        Returns:
            HttpResponse: The HTTP response with a success message and status code 200.
        """
        user = Player.objects.get(api_user_id=user_data['api_user_id'])
        login(request, user)
        logger.info('User %s logged in successfully', user.username)
        return self._response_with_message('Login successful', status.HTTP_200_OK)

    def _create_user(self, request, user_data):
        """
        Create a user with the given user data.

        Args:
            request (HttpRequest): The HTTP request object.
            user_data (dict): The user data containing the necessary information.

        Returns:
            HttpResponse: The HTTP response with a success message and status code 201.
        """
        player = create_player(user_data)
        logger.info('Player %s created successfully', player.username)
        return self._response_with_message('User created successfully', status.HTTP_201_CREATED)

    def _get_access_token(self, code):
        """
        Retrieves the access token from the 42 API using the provided code.

        Args:
            code (str): The authorization code obtained from the user.

        Returns:
            str: The access token if successful, None otherwise.
        """
        try:
            token_response = get_42_tokens(code)
            return token_response.get('access_token')
        except Exception as e:
            logger.error('Error retrieving access token: %s', str(e))
            return None

    def _response_with_message(self, message, status_code):
        """
        Returns a response with the given message and status code.

        Args:
            message (str): The message to include in the response.
            status_code (int): The HTTP status code for the response.

        Returns:
            Response: The response object containing the message and status code.
        """
        logger.debug(message)
        return Response({'message': message}, status=status_code)


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
