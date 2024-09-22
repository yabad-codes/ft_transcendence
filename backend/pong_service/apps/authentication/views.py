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
from .helpers import (
    set_cookie,
    error_response,
)

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