
async def get_user_from_access_token(access_token):
    from django.conf import settings
    from pong_service.apps.authentication.models import Player
    from jwt import InvalidTokenError
    from rest_framework_simplejwt.exceptions import TokenError
    from jwt import decode as jwt_decode
    from asgiref.sync import sync_to_async
    try:
        decoded_token = await sync_to_async(jwt_decode)(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')

        if user_id is None:
            return None

        user = await sync_to_async(Player.objects.get)(id=user_id)
        return user
    except (TokenError, InvalidTokenError, Player.DoesNotExist):
        return None
