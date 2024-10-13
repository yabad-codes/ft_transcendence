from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.utils.timezone import make_aware, now as django_now
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.conf import settings
from .helpers import set_cookie
import pytz
import jwt

class TokenRefreshMiddleware:
    """
    Middleware for automatically refreshing JWT tokens.

    This middleware checks the validity of access and refresh tokens in cookies,
    refreshing them when necessary to maintain a seamless authentication experience.
    """
    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response
        self.User = get_user_model()
        self.TOKEN_REFRESH_THRESHOLD = getattr(settings, 'TOKEN_REFRESH_THRESHOLD', 2)
    
    def _is_token_expired(self, expiration_time):
        """
        Check if a token is close to expiration.
        """
        return expiration_time <= django_now() + timedelta(minutes=self.TOKEN_REFRESH_THRESHOLD)
    
    def _delete_tokens(self, response):
        """
        Delete authentication and refresh tokens from cookies.
        """
        response.delete_cookie(settings.AUTH_COOKIE)
        response.delete_cookie(settings.REFRESH_COOKIE)
        return response
    
    def _is_valid_access_token(self, access_token):
        """
        Check if an access token is valid.
        """
        try:
            access_token_obj = AccessToken(access_token)
            exp = access_token_obj.get('exp')
            expiration = make_aware(datetime.fromtimestamp(exp), timezone=pytz.UTC)
            return not self._is_token_expired(expiration)
        except (TokenError, InvalidToken, jwt.DecodeError):
            return False
    
    def _refresh_tokens(self, refresh_token):
        """
        Refresh the access and refresh tokens.
		"""
        refresh = RefreshToken(refresh_token)
        user_id = refresh.get('user_id')
        if user_id is None:
            raise InvalidToken("Invalid refresh token: no user_id")
        user = self.User.objects.get(id=user_id)
        new_refresh = RefreshToken.for_user(user)
        refresh.blacklist()
        return {
            'access': str(new_refresh.access_token),
            'refresh': str(new_refresh)
        }
    
    def _set_token_cookies(self, response, tokens):
        """
        Set the access and refresh tokens as cookies.
        """
        response = set_cookie(
            response,
            settings.AUTH_COOKIE,
            tokens['access'],
            settings.AUTH_COOKIE_ACCESS_MAX_AGE
        )
        response = set_cookie(
            response,
            settings.REFRESH_COOKIE,
            tokens['refresh'],
            settings.AUTH_COOKIE_REFRESH_MAX_AGE
        )
        return response
    
    def _handle_invalid_access_token(self, request, refresh_token):
        """
        Handle an invalid access token by attempting to refresh the tokens.
        """
        try:
            new_tokens = self._refresh_tokens(refresh_token)
            request.COOKIES[settings.AUTH_COOKIE] = new_tokens['access']
            response = self.get_response(request)
            return self._set_token_cookies(response, new_tokens)
        except (TokenError, InvalidToken, jwt.DecodeError, self.User.DoesNotExist):
            return self._delete_tokens(self.get_response(request))
        
    def __call__(self, request):
        """
        Process the request and refresh tokens if necessary.
        """
        access_token = request.COOKIES.get(settings.AUTH_COOKIE)
        refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE)

        if access_token and self._is_valid_access_token(access_token):
            return self.get_response(request)
        if refresh_token:
            return self._handle_invalid_access_token(request, refresh_token)

        return self.get_response(request)
