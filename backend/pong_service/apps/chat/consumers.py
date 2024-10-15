import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from pong_service.helpers import get_user_from_access_token
from django.db.models import Q
from django.conf import settings


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.cookies = self.scope['cookies']
        self.access_token = self.cookies.get(settings.AUTH_COOKIE)
        self.user = await get_user_from_access_token(self.access_token)

        if self.user is None:
            await self.close()
            return None

        self.room_name = f'chat_{self.user.id}'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if self.user is None:
            return None

        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))


def send_message(user_id, conversationID, message):
    channel_layer = get_channel_layer()

    if not channel_layer:
        # Log error or raise an exception as needed
        print("Channel layer is not available.")
        return

    try:
        async_to_sync(channel_layer.group_send)(
            f'chat_{user_id}',
            {
                'type': 'chat_message',
                'message': {
                    'conversation_id': conversationID,
                    'data': message
                }
            }
        )
    except Exception as e:
        # Handle exceptions, possibly logging or retrying
        print(f"Failed to send message via WebSocket: {e}")


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # settings.configure()

        self.cookies = self.scope['cookies']
        self.access_token = self.cookies.get(settings.AUTH_COOKIE)
        self.user = await get_user_from_access_token(self.access_token)

        if self.user is None:
            await self.close()
            return None

        self.room_name = f'notification_{self.user.id}'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

        self.user.online = True
        await sync_to_async(self.user.save)()
        await self.sendOnlineStatusToFriends()

    async def disconnect(self, close_code):
        from pong_service.apps.authentication.models import Player
        from pong_service.apps.pong.models import GameRequest

        if self.user is None:
            return None

        # Check if the user in a game request and remove it
        game_request = await sync_to_async(GameRequest.objects.filter)(Q(requester=self.user) | Q(opponent=self.user))
        if await sync_to_async(game_request.exists)():
            await sync_to_async(game_request.delete)()

        player = await sync_to_async(Player.objects.get)(id=self.user.id)
        player.online = False
        self.user.online = False
        await sync_to_async(player.save)()
        await self.sendOnlineStatusToFriends()

        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def notification_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def sendOnlineStatusToFriends(self):
        from pong_service.apps.chat.models import Friendship

        friends = await sync_to_async(list)(Friendship.objects.filter(
            Q(player1=self.user, friendshipAccepted=True) |
            Q(player2=self.user, friendshipAccepted=True)
        ).values_list('player1_id', 'player2_id'))

        for friend in friends:
            friend_id = friend[1] if friend[0] == self.user.id else friend[0]
            await self.channel_layer.group_send(
                f'notification_{friend_id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'online_status',
                        'username': self.user.username,
                        'online': self.user.online
                    }
                }
            )

    @staticmethod
    def sendFriendRequestNotification(user_id, friend_id):
        channel_layer = get_channel_layer()

        if not channel_layer:
            # Log error or raise an exception as needed
            print("Channel layer is not available.")
            return

        try:
            async_to_sync(channel_layer.group_send)(
                f'notification_{friend_id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'friend_request',
                        'user_id': user_id
                    }
                }
            )
        except Exception as e:
            # Handle exceptions, possibly logging or retrying
            print(f"Failed to send message via WebSocket: {e}")

    @staticmethod
    def sendGameRequestNotification(user_id, opponent_id, request_id):
        channel_layer = get_channel_layer()

        if not channel_layer:
            # Log error or raise an exception as needed
            print("Channel layer is not available.")
            return

        try:
            async_to_sync(channel_layer.group_send)(
                f'notification_{opponent_id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'game_request',
                        'request_id': request_id,
                        'requester_name': user_id.username,
                        'avatar_url': user_id.avatar_url,
                    }
                }
            )
        except Exception as e:
            # Handle exceptions, possibly logging or retrying
            print(f"Failed to send message via WebSocket: {e}")
    
    @staticmethod
    def sendGameRequestResponseNotification(requester_id, game_id):
        channel_layer = get_channel_layer()

        if not channel_layer:
            # Log error or raise an exception as needed
            print("Channel layer is not available.")
            return

        try:
            async_to_sync(channel_layer.group_send)(
                f'notification_{requester_id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'game_request_response',
                        'game_id': game_id,
                    }
                }
            )
        except Exception as e:
            # Handle exceptions, possibly logging or retrying
            print(f"Failed to send message via WebSocket: {e}")
            
    @staticmethod
    def sendTournamentNotification(player):
        channel_layer = get_channel_layer()

        if not channel_layer:
            # Log error or raise an exception as needed
            print("Channel layer is not available.")
            return

        try:
            async_to_sync(channel_layer.group_send)(
                f'notification_{player.id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'tournament',
                    }
                }
            )
        except Exception as e:
            # Handle exceptions, possibly logging or retrying
            print(f"Failed to send message via WebSocket: {e}")
