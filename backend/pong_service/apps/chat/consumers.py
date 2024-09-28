import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from pong_service.helpers import get_user_from_access_token
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
		# text_data_json = json.loads(text_data)
		# message = text_data_json['message']
		# await self.channel_layer.group_send(
		# 	self.room_group_name,
		# 	{
		# 		'type': 'chat_message',
		# 		'message': message
		# 	}
		# )
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
