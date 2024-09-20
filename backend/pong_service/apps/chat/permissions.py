from rest_framework import permissions
from .models import Conversations, Messages

class IsParticipantInConversation(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the object is a Conversation or a Message
        if isinstance(obj, Conversations):
            # If it's a Conversation, check if the user is one of the participants
            return obj.player1 == request.user or obj.player2 == request.user
        elif isinstance(obj, Messages):
            # If it's a Message, check the conversation associated with the message
            conversation = obj.atConversation
            return conversation.player1 == request.user or conversation.player2 == request.user
        return False
