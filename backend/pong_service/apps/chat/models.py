from django.db import models
from pong_service.apps.authentication.models import Player

# Create your models here.

class Conversations(models.Model):
	conversationID = models.BigAutoField(primary_key=True)
	player1 = models.ForeignKey(Player, models.SET_NULL, null=True, related_name='conversations_as_player1')
	player2 = models.ForeignKey(Player, models.SET_NULL, null=True, related_name='conversations_as_player2')
	lastMessage = models.ForeignKey('Messages', models.SET_NULL, null=True)
	IsVisibleToPlayer1 = models.BooleanField(default=True)
	IsVisibleToPlayer2 = models.BooleanField(default=True)
	IsBlockedByPlayer1 = models.BooleanField(default=False)
	IsBlockedByPlayer2 = models.BooleanField(default=False)
	lastMessageTimeStamp = models.DateTimeField(auto_now=True)

class Messages(models.Model):
	messageID = models.BigAutoField(primary_key=True)
	atConversation = models.ForeignKey(Conversations, on_delete=models.CASCADE)
	sender = models.ForeignKey(Player, models.SET_NULL, null=True)
	content = models.TextField()
	IsVisibleToPlayer1 = models.BooleanField(default=True)
	IsVisibleToPlayer2 = models.BooleanField(default=True)
	messageTimestamp = models.DateTimeField(auto_now_add=True)

class MessageReadStatus(models.Model):
	messageReadStatusID = models.BigAutoField(primary_key=True)
	atMessage = models.ForeignKey(Messages, on_delete=models.CASCADE)
	receiver = models.ForeignKey(Player, on_delete=models.CASCADE)
	IsRead = models.BooleanField(default=False)

class Friendship(models.Model):
	friendshipID = models.BigAutoField(primary_key=True)
	player1 = models.ForeignKey(Player, models.CASCADE, related_name='friendships_as_player1')
	player2 = models.ForeignKey(Player, models.CASCADE, related_name='friendships_as_player2')
	friendshipTimestamp = models.DateTimeField(auto_now_add=True)
	friendshipAccepted = models.BooleanField(default=False)

class BlockedUsers(models.Model):
	blockID = models.BigAutoField(primary_key=True)
	player = models.ForeignKey(Player, models.CASCADE)
	blockedUser = models.ForeignKey(Player, models.CASCADE, related_name='blocked_user')
	blockTimestamp = models.DateTimeField(auto_now_add=True)
