from rest_framework.generics import CreateAPIView, ListAPIView
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
from pong_service.permissions import IsUnauthenticated

from pong_service.apps.chat.models import BlockedUsers
from django.db.models import Q
from django.http import Http404
from .helpers import set_cookie
from urllib.parse import urlencode

from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .forms import TwoFactorAuthForm, BackupCodeForm
import qrcode
import io
import base64
import jwt
from .helpers import (
    set_cookie,
    error_response,
    handle_successful_verification
)
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class OAuthLoginView(APIView):
    permission_classes = (IsUnauthenticated,)

    def get(self, request):
        logger.debug('Initiating OAuth login')
        auth_url = f"{settings.AUTH_URL}"
        return Response({'auth_url': auth_url}, status=status.HTTP_200_OK)
    
class OAuthCallbackView(APIView):
    permission_classes = (IsUnauthenticated,)

    def get(self, request):
        logger.debug('Received OAuth callback')

        code = request.GET.get('code')
        if not code:
            # return self._response_with_message('No code in request', status.HTTP_400_BAD_REQUEST)
            return self._error_redirect('Authorization failed')
        
        access_token = self._get_access_token(code)
        if not access_token:
            # return self._response_with_message('Failed to get access token', status.HTTP_400_BAD_REQUEST)
            return self._error_redirect('Failed to get access token')
        
        user_data = helpers.get_42_user_data(access_token)
        if not user_data:
            # return self._response_with_message('Failed to get user data', status.HTTP_400_BAD_REQUEST)
            return self._error_redirect('Failed to get user data')
        
        user_data = helpers.construct_user_data(user_data)
        try:
            if helpers.user_already_exists(user_data):
                return self._login_user(request, user_data)
            return self._create_user(request, user_data)
        except IntegrityError as e:
            # return self._response_with_message('Failed to create user', status.HTTP_400_BAD_REQUEST)
            return self._error_redirect('Failed to create user')
        except KeyError as e:
            # return self._response_with_message('Failed to get user data', status.HTTP_400_BAD_REQUEST)
            return self._error_redirect('Failed to get user data')
        except Exception as e:
            # return self._response_with_message('An error occurred', status.HTTP_500_INTERNAL_SERVER_ERROR)
            return self._error_redirect('An error occurred')

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
        # response = JsonResponse({'status': 'success', 'message': 'Login successful'})
        response = self._success_redirect('Login successful')
        print("Response: ", response)
        helpers.set_cookie(response, 'access', access_token, settings.AUTH_COOKIE_ACCESS_MAX_AGE)
        helpers.set_cookie(response, 'refresh', refresh_token, settings.AUTH_COOKIE_REFRESH_MAX_AGE)
        logger.debug('User %s logged in successfully', user.username)
        return response

    def _create_user(self, request, user_data):
        player = helpers.create_player(user_data)
        logger.debug('User %s created successfully', player.username)
        return self._login_user(request, user_data)

    def _success_redirect(self, message):
        params = urlencode({
            'status': 'success',
            'message': message,
        })
        print(f'{settings.FRONTEND_URL}/oauth-callback?{params}')
        return redirect(f'{settings.FRONTEND_URL}/oauth-callback?{params}')

    def _error_redirect(self, message):
        params = urlencode({
            'status': 'error',
            'message': message
        })
        print(f'{settings.FRONTEND_URL}/oauth-callback?{params}')
        return redirect(f'{settings.FRONTEND_URL}/oauth-callback?{params}')

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
        response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        response = helpers.set_cookie(response, 'access', '', 0)
        response = helpers.set_cookie(response, 'refresh', '', 0)
        return response

class LoginView(TokenObtainPairView):
    """
    View for handling user login with JWT authentication.
    """
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
            """
            Handle the HTTP POST request for user login.

            Args:
                request (HttpRequest): The HTTP request object.
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                HttpResponse: The HTTP response object.
            """
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                response = super().post(request, *args, **kwargs)

                if response.status_code == status.HTTP_200_OK:
                    player = Player.objects.get(username=request.data['username'])
                    if player.two_factor_enabled:
                        request.session['temp_access_token'] = response.data['access']
                        request.session['temp_refresh_token'] = response.data['refresh']
                        return Response({'require_2fa': True}, status=status.HTTP_202_ACCEPTED)
                    
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
                return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
            {"error": "Invalid data."},
            status=status.HTTP_400_BAD_REQUEST
            )
    


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
            return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
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
    
    def get(self, request):
        """
        Handle GET request to list all players.

        :param request: The HTTP request object.
        :return: A Response object with the serialized player data.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Create a dictionary structure for the response
        response_data = {
            'data': serializer.data,  # Player data from the serializer
            'success': True  # Add success field inside the response
        }

        return Response(response_data, status=status.HTTP_200_OK)

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

class SetupTwoFactorView(APIView):
    """
	API view for setting up two-factor authentication (2FA).
 
	This view handles the setup of 2FA for a player. It generates a 2FA secret for the player,
	generates a QR code for the player to scan with their 2FA app, and returns the secret and QR code.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        player = request.user
        if not player.two_factor_secret:
            player.two_factor_secret = player.generate_two_factor_secret()
            player.save()
        totp = player.get_totp()
        qr = qrcode.make(totp.provisioning_uri(player.username, issuer_name="Pong Talk"))
        buffered = io.BytesIO()
        qr.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return Response({
            'secret': player.two_factor_secret,
            'qr_code': f"data:image/png;base64,{qr_base64}"
        })
        
    def post(self, request):
        form = TwoFactorAuthForm(request.data)
        if not form.is_valid():
            return error_response(form.errors, status.HTTP_400_BAD_REQUEST)
        player = request.user
        if player.verify_two_factor_code(form.cleaned_data['code']):
            player.two_factor_enabled = True
            player.backup_codes = player.generate_backup_codes()
            player.save()
            return Response({'success': True, 'backup_codes': player.backup_codes})
        else:
            return error_response({'error': 'Invalid code'}, status.HTTP_400_BAD_REQUEST)

class DisableTwoFactorView(APIView):
    """
	API view for disabling two-factor authentication (2FA).
 
	This view handles the disabling of 2FA for a player. It sets the player's two_factor_enabled field to False,
	clears the two_factor_secret and backup_codes fields, and saves the player object.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        player = request.user
        player.two_factor_enabled = False
        player.two_factor_secret = None
        player.backup_codes = []
        player.save()
        return Response({'success': True})

class BaseTwoFactorView(APIView):
    """
    Base API view for verifying two-factor authentication (2FA) codes.

    This view handles the common functionality of verifying 2FA codes submitted by users during the authentication process.
    It validates the submitted code, retrieves the player object, and upon successful verification,
    sets the access and refresh tokens in the response cookies.
    """
    permission_classes = [AllowAny]

    def handle_token_verification(self, request):
        access_token = request.session.get('temp_access_token')
        if not access_token:
            return error_response('Authentication required', status.HTTP_401_UNAUTHORIZED)
        
        try:
            decode_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            username = decode_token.get('username')
            
            if not username:
                return error_response('Username is required', status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError:
            return error_response('Token expired', status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return error_response('Invalid token', status.HTTP_401_UNAUTHORIZED)
        
        return username

    def handle_player_retrieval(self, username):
        try:
            player = Player.objects.get(username=username)
        except Player.DoesNotExist:
            return error_response('Player not found', status.HTTP_404_NOT_FOUND)
        
        return player


class VerifyTwoFactorView(BaseTwoFactorView):
    """
    API view for verifying two-factor authentication (2FA) codes.
    """
    def post(self, request):
        username = self.handle_token_verification(request)
        if isinstance(username, Response):
            return username

        form = TwoFactorAuthForm(request.data)
        if not form.is_valid():
            return error_response(form.errors, status.HTTP_400_BAD_REQUEST)
        
        player = self.handle_player_retrieval(username)
        if isinstance(player, Response):
            return player

        if not player.verify_two_factor_code(form.cleaned_data['code']):
            return error_response('Invalid 2FA code', status.HTTP_400_BAD_REQUEST)
        
        return handle_successful_verification(request)


class UseBackupCodeView(BaseTwoFactorView):
    """
    API view for using a backup code to verify 2FA.
    """
    def post(self, request):
        username = self.handle_token_verification(request)
        if isinstance(username, Response):
            return username

        form = BackupCodeForm(request.data)
        if not form.is_valid():
            return error_response(form.errors, status.HTTP_400_BAD_REQUEST)

        player = self.handle_player_retrieval(username)
        if isinstance(player, Response):
            return player

        if not player.use_backup_code(form.cleaned_data['code']):
            return error_response('Invalid backup code', status.HTTP_400_BAD_REQUEST)

        return handle_successful_verification(request)

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
            return Response({"message":"update info successfully", "success": True}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors, "success": False}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"message":"update avatar successfully", "success": True}, status=status.HTTP_200_OK)
        return Response({"errors": serializers.errors, "success": False}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"message":"update password successfully", "success": True}, status=status.HTTP_200_OK)
            return Response({"errors": serializers.errors, "success": False}, status=status.HTTP_400_BAD_REQUEST)

class CheckTwoFactorView(APIView):
	"""
	API view for checking if 2FA is enabled for a player.
 
	This view checks if 2FA is enabled for a player and returns a boolean value indicating the status.
	"""
	permission_classes = [IsAuthenticated]
	def get(self, request):
		player = request.user
		return Response({'two_factor_enabled': player.two_factor_enabled})

class UserDetailsView(APIView):
	"""
	API view for getting user details.
	Requires authentication.
	"""
	permission_classes = [IsAuthenticated]

	def get(self, request):
		"""
		Handle GET request to get user details.

		Parameters:
		- request: The HTTP request object.

		Returns:
		- Response: The HTTP response object.
		"""
		user = request.user
		return Response({
			"success": True,
			"username": user.username,
			"first_name": user.first_name,
			"last_name": user.last_name,
			"user_id": user.id,
			"avatar": user.avatar_url if user.avatar_url else None
		})