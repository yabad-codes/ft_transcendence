from rest_framework.generics import ListCreateAPIView, ListAPIView
from .serializers import *
from .models import Player
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from pong_service.permissions import IsUnauthenticated
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView
)
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

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining a new access and refresh token pair.
    
    Args:
		TokenObtainPairView: The default view for obtaining a new access and refresh token pair.
	
	Returns:
		Response: A response object with the new access and refresh tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to obtain a new access and refresh token pair.
		1. Call the parent class's post method to obtain the tokens.
		2. If the response status code is 200, set the tokens in cookies.
        """
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
    permission_classes = (IsUnauthenticated,)


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

class VerifyTwoFactorView(APIView):
    """
    API view for verifying two-factor authentication (2FA) codes.

    This view handles the verification of 2FA codes submitted by users during the authentication process.
    It validates the submitted code, retrieves the player object, and upon successful verification,
    sets the access and refresh tokens in the response cookies.
    """
    permission_classes = [AllowAny]
    def post(self, request):
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
        
        form = TwoFactorAuthForm(request.data)
        if not form.is_valid():
            return error_response(form.errors, status.HTTP_400_BAD_REQUEST)
        
        try:
            player = Player.objects.get(username=username)
        except Player.DoesNotExist:
            return error_response('Player not found', status.HTTP_404_NOT_FOUND)
        
        if not player.verify_two_factor_code(form.cleaned_data['code']):
            return error_response('Invalid 2FA code', status.HTTP_400_BAD_REQUEST)
        
        return handle_successful_verification(request)

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

class UseBackupCodeView(APIView):
    """
	API view for using a backup code to verify 2FA.
 
	This view handles the verification of a 2FA code using a backup code. It validates the code,
	retrieves the player object, and upon successful verification, sets the access and refresh tokens in the response cookies.
    """
    permission_classes = [AllowAny]
    def post(self, request):
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
        
        form = BackupCodeForm(request.data)
        if form.is_valid():
            player = Player.objects.get(username=username)
            if player.use_backup_code(form.cleaned_data['code']):
                response = Response({'success': True})
                response = set_cookie(
                    response,
                    'access',
                    request.session['temp_access_token'],
                    settings.AUTH_COOKIE_ACCESS_MAX_AGE
                )
                response = set_cookie(
                    response,
                    'refresh',
                    request.session['temp_refresh_token'],
                    settings.AUTH_COOKIE_REFRESH_MAX_AGE
                )
                del request.session['temp_access_token']
                del request.session['temp_refresh_token']
                return response
            else:
                return Response({'error': 'Invalid backup code'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)