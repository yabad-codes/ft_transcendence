from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils.timezone import make_aware, now as django_now
from rest_framework_simplejwt.exceptions import TokenError
from datetime import datetime, timedelta
from django.conf import settings
import pytz

class TokenRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get(settings.AUTH_COOKIE)
        refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE)
        
        if access_token:
            try:
                access_token_obj = AccessToken(access_token)
                exp = access_token_obj.get('exp')
                
                # Convert the timestamp to an offset-aware datetime object
                expiration = make_aware(datetime.fromtimestamp(exp), timezone=pytz.UTC)
                
                if expiration > django_now() + timedelta(minutes=2):
                    return self.get_response(request)
                else:
                    raise TokenError("Token near expiration")
            except TokenError:
                pass

        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                request.COOKIES[settings.AUTH_COOKIE] = new_access_token
                response = self.get_response(request)
                
                response.set_cookie(
                    key=settings.AUTH_COOKIE,
                    value=new_access_token,
                    max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                    secure=settings.AUTH_COOKIE_SECURE,
                    httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                    samesite=settings.AUTH_COOKIE_SAMESITE,
                    path=settings.AUTH_COOKIE_PATH
                )
                return response
            except TokenError:
                response = self.get_response(request)
                response.delete_cookie(settings.AUTH_COOKIE)
                response.delete_cookie(settings.REFRESH_COOKIE)
                return response

        return self.get_response(request)