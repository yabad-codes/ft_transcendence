from rest_framework.generics import ListCreateAPIView, ListAPIView
from .serializers import *
from .models import Player
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.conf import settings

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data['access']
            response.set_cookie(
				key='access',
				value=access,
				max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
				secure=settings.AUTH_COOKIE_SECURE,
				httponly=settings.AUTH_COOKIE_HTTP_ONLY,
				samesite=settings.AUTH_COOKIE_SAMESITE,
				path=settings.AUTH_COOKIE_PATH
			)
            refresh = response.data['refresh']
            response.set_cookie(
                key='refresh',
                value=refresh,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE,
                path=settings.AUTH_COOKIE_PATH
			)
        return response

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('refresh')
        if refresh is not None:
            request.data['refresh'] = refresh
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data['access']
            response.set_cookie(
				key='access',
				value=access,
				max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
				secure=settings.AUTH_COOKIE_SECURE,
				httponly=settings.AUTH_COOKIE_HTTP_ONLY,
				samesite=settings.AUTH_COOKIE_SAMESITE,
				path=settings.AUTH_COOKIE_PATH
			)
        return response
            
class CustomTokenVerifyView(TokenVerifyView):
	def post(self, request, *args, **kwargs):
		access = request.COOKIES.get('access')
		if access:
			request.data['token'] = access
		return super().post(request, *args, **kwargs)

class LogoutView(APIView):
    def post(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response


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


