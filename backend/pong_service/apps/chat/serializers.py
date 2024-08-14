from .models import *
from rest_framework import serializers


class MessageReadStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = MessageReadStatus
        fields = '__all__'


class MessagesSerializer(serializers.ModelSerializer):
    read_status = MessageReadStatusSerializer(many=True, read_only=True)

    class Meta:
        model = Messages
        fields = ['messageID', 'atConversation', 'sender', 'content',
                  'IsVisibleToPlayer1', 'IsVisibleToPlayer2', 'messageTimestamp', 'read_status']
        read_only_fields = ['atConversation', 'sender', 'IsVisibleToPlayer1', 'IsVisibleToPlayer2']


class ConversationSerializer(serializers.ModelSerializer):
    last_message = MessagesSerializer(source='lastMessage', read_only=True)

    class Meta:
        model = Conversations
        fields = ['conversationID', 'player1', 'player2',
                  'last_message', 'lastMessageTimeStamp']
        read_only_fields = ['player1']

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = '__all__'
        read_only_fields = ['player1','friendshipTimestamp', 'friendshipAccepted', 'friendshipRejected']
