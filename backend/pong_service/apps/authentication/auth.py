from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Authenticate the request using JWT token stored in a cookie.

        This method overrides the default JWT authentication to use cookies
        instead of the Authorization header.

        Args:
            request: The incoming request object.

        Returns:
            A tuple of (user, token) if authentication is successful, where
            user is the authenticated user instance and token is the validated
            JWT token.
            None if authentication fails.

        Raises:
            No exceptions are raised as they are caught and handled internally.
        """
        try:
            # Attempt to get the raw JWT token from the cookie
            raw_token = request.COOKIES.get(settings.AUTH_COOKIE)
            # If no token is found in the cookie, return None
            if raw_token is None:
                return None
            # Validate the token
            validated_token = self.get_validated_token(raw_token)
            # Get the user associated with the token and return the user-token pair
            return self.get_user(validated_token), validated_token
        except:
            # If any exception occurs during the process, return None
            # This could be due to an invalid token, expired token, etc.
            return None