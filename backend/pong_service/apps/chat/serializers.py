from .models import *
from rest_framework import serializers
from pong_service.apps.authentication.serializers import PlayerListSerializer
from django.db.models import Q


class MessageReadStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = MessageReadStatus
        fields = '__all__'


class MessagesSerializer(serializers.ModelSerializer):
    read_status = MessageReadStatusSerializer(many=True, read_only=True)
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Messages
        fields = ['messageID', 'atConversation', 'sender', 'content',
                  'IsVisibleToPlayer1', 'IsVisibleToPlayer2', 'messageTimestamp', 'read_status']
        read_only_fields = ['atConversation', 'sender',
                            'IsVisibleToPlayer1', 'IsVisibleToPlayer2']

    def get_sender(self, obj):
        return obj.sender.username


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_messages_count = serializers.SerializerMethodField()
    player1 = PlayerListSerializer(read_only=True)
    player2 = PlayerListSerializer(read_only=True)
    IsBlockedByMe = serializers.SerializerMethodField()
    IsBlockedByOtherPlayer = serializers.SerializerMethodField()
    player2_username = serializers.CharField(write_only=True)

    class Meta:
        model = Conversations
        fields = ['conversationID', 'player1', 'player2', 'player2_username', 'IsVisibleToPlayer1', 'IsVisibleToPlayer2', 'IsBlockedByMe', 'IsBlockedByOtherPlayer',
                  'last_message', 'unread_messages_count', 'lastMessageTimeStamp']
        read_only_fields = ['player1',
                            'IsVisibleToPlayer1', 'IsBlockedByPlayer1', 'IsBlockedByPlayer2' ,'IsVisibleToPlayer2']

    def get_IsBlockedByMe(self, obj):
        user = self.context['request'].user
        if obj.player1 == user:
            return obj.IsBlockedByPlayer1
        else:
            return obj.IsBlockedByPlayer2
    
    def get_IsBlockedByOtherPlayer(self, obj):
        user = self.context['request'].user
        if obj.player1 == user:
            return obj.IsBlockedByPlayer2
        else:
            return obj.IsBlockedByPlayer1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              

    def get_last_message(self, obj):
        # Ensure we're working with a Conversations instance
        if isinstance(obj, Conversations):
            user = self.context['request'].user
            if obj.lastMessage:
                if (user == obj.player1 and obj.lastMessage.IsVisibleToPlayer1) or \
                        (user == obj.player2 and obj.lastMessage.IsVisibleToPlayer2):
                    return obj.lastMessage.content
            return None

        # Handle cases where obj is not an instance of Conversations
        raise TypeError(f"Expected Conversations instance but got {type(obj)}")

    def get_unread_messages_count(self, obj):
        if isinstance(obj, Conversations):
            user = self.context['request'].user
            unread_messages_count = MessageReadStatus.objects.filter(
                Q(atMessage__atConversation=obj) &
                Q(receiver=user) &
                Q(IsRead=False)
            ).count()
            return unread_messages_count

        raise TypeError(f"Expected Conversations instance but got {type(obj)}")

    def create(self, validated_data):
        player1 = self.context['request'].user
        player2_username = validated_data.pop('player2_username')

        # Look up player2 by username
        try:
            player2 = Player.objects.get(username=player2_username)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                'Player with the provided username does not exist.')

        conversation = Conversations.objects.create(
            player1=player1, player2=player2)
        return conversation


class FriendshipSerializer(serializers.ModelSerializer):
    player1 = PlayerListSerializer(read_only=True)
    player2 = PlayerListSerializer(read_only=True)

    player2_username = serializers.CharField(write_only=True)

    class Meta:
        model = Friendship
        fields = '__all__'
        read_only_fields = ['player1', 'friendshipTimestamp',
                            'friendshipAccepted']

    def create(self, validated_data):
        player1 = self.context['request'].user
        player2_username = validated_data.pop('player2_username')
        try:
            player2 = Player.objects.get(username=player2_username)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                'Player with the provided username does not exist.')
        friendship = Friendship.objects.create(
            player1=player1, player2=player2)
        return friendship
