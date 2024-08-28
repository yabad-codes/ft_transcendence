from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsParticipantInConversation
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.http import Http404

# Create your views here.


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations between players.

    This ViewSet provides the following actions:
    - list: Get a list of conversations where the authenticated user is a participant.
    - retrieve: Get details of a specific conversation.
    - create: Create a new conversation between the authenticated user and another player.

    Only authenticated users who are participants in the conversation can perform these actions.
    """

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantInConversation]

    def get_queryset(self):
        """
        Returns the queryset of conversations for the current user.

        The queryset includes conversations where the current user is either player1 or player2.
        The conversations are ordered by the timestamp of the last message in descending order.
        """
        user = self.request.user
        return Conversations.objects.filter(models.Q(player1=user, IsVisibleToPlayer1=True) |
                                            models.Q(player2=user, IsVisibleToPlayer2=True)).order_by('-lastMessageTimeStamp')

    def get_object(self):
        """
        Retrieve the conversation object for the current request.

        This method overrides the get_object method of the parent class
        to add permission checks before returning the conversation object.

        Returns:
            The conversation object for the current request.
        """
        conversation = super().get_object()
        self.check_object_permissions(self.request, conversation)
        return conversation

    def perform_create(self, serializer):
        """
        Perform the creation of a conversation.

        Args:
            serializer (Serializer): The serializer instance.

        Raises:
            ValidationError: If player2 is not provided or if a conversation already exists between the two players.

        Returns:
            None
        """
        user = self.request.user
        player2_username = self.request.data.get('player2_username')

        # Ensure player2_username is provided
        if not player2_username:
            raise serializers.ValidationError(
                'player2_username is required to create a conversation.')

        # Look up player2 by username
        try:
            player2 = Player.objects.get(username=player2_username)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                'Player with the provided username does not exist.')

        # Check if a conversation already exists between these two players
        existing_conversation = Conversations.objects.filter(
            models.Q(player1=user, player2=player2) |
            models.Q(player1=player2, player2=user)
        ).first()

        if existing_conversation:
            # If conversation exists, update its visibility
            if user == existing_conversation.player1:
                existing_conversation.IsVisibleToPlayer1 = True
            elif user == existing_conversation.player2:
                existing_conversation.IsVisibleToPlayer2 = True
            existing_conversation.save()

            
            # Update the serializer instance with the existing conversation
            serializer.instance = existing_conversation
        else:
            # Create the new conversation if it doesn't exist
            serializer.save(player1=user, player2=player2)


class MessageListCreateAPI(generics.ListCreateAPIView):
    """
    API view for listing and creating messages in a conversation.

    This API view provides the following actions:
    - list: Get a list of messages in a conversation.
    - create: Create a new message in a conversation.

    Only authenticated users who are participants in the conversation can perform these actions.
    """
    serializer_class = MessagesSerializer
    permission_classes = [IsAuthenticated, IsParticipantInConversation]

    def get_queryset(self):
        """
        Returns the queryset of messages for a specific conversation.

        This method retrieves the user, conversation ID, and conversation object.
        It checks the object permissions for the conversation and marks all unread
        messages as read. Finally, it filters and returns the messages based on
        the visibility criteria for the current user.

        Returns:
            QuerySet: The queryset of messages for the conversation.
        """
        user = self.request.user
        conversation_id = self.kwargs['conversation_id']
        # conversation = Conversations.objects.get(pk=conversation_id)
        conversation = get_object_or_404(Conversations, pk=conversation_id)

        self.check_object_permissions(self.request, conversation)
        # Mark all unread messages as read
        MessageReadStatus.objects.filter(
            atMessage__atConversation=conversation,
            receiver=user,
            IsRead=False
        ).update(IsRead=True)

        # Check if the conversation is visible to the user
        if (user == conversation.player1 and not conversation.IsVisibleToPlayer1) or \
                (user == conversation.player2 and not conversation.IsVisibleToPlayer2):
            raise Http404("Conversation not found or has been deleted.")

        if user == conversation.player1:
            return Messages.objects.filter(atConversation=conversation, IsVisibleToPlayer1=True)
        else:
            return Messages.objects.filter(atConversation=conversation, IsVisibleToPlayer2=True)

    def perform_create(self, serializer):
        """
        Perform the creation of a new message in a conversation.

        Args:
            serializer (Serializer): The serializer instance.

        Returns:
            None
        """
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversations, pk=conversation_id)

        # Check if the conversation is visible to the user
        if (self.request.user == conversation.player1 and not conversation.IsVisibleToPlayer1) or \
                (self.request.user == conversation.player2 and not conversation.IsVisibleToPlayer2):
            raise Http404("Conversation not found or has been deleted.")

        serializer.save(sender=self.request.user,
                        atConversation=conversation)

        # Update last message
        conversation.lastMessage = serializer.instance

        # Check if the other player's visibility needs to be reset
        if self.request.user == conversation.player1 and not conversation.IsVisibleToPlayer2:
            conversation.IsVisibleToPlayer2 = True
        elif self.request.user == conversation.player2 and not conversation.IsVisibleToPlayer1:
            conversation.IsVisibleToPlayer1 = True

        conversation.save()


class ConversationClearView(APIView):
    """
    API view for clearing a conversation.

    This API view provides the following action:
    - post: Clear a conversation by marking all messages as not visible to the authenticated user.

    Only authenticated users who are participants in the conversation can perform this action.
    """
    permission_classes = [IsAuthenticated, IsParticipantInConversation]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversations, pk=conversation_id)
        user = request.user

        self.check_object_permissions(request, conversation)
        if user == conversation.player1:
            Messages.objects.filter(atConversation=conversation).update(
                IsVisibleToPlayer1=False)
        else:
            Messages.objects.filter(atConversation=conversation).update(
                IsVisibleToPlayer2=False)

        # Delete all messages that are not visible to both players
        Messages.objects.filter(atConversation=conversation,
                                IsVisibleToPlayer1=False, IsVisibleToPlayer2=False).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ConversationDeleteView(APIView):
    """
    API view for deleting a conversation.

    This API view provides the following action:
    - post: Delete a conversation for the authenticated user.

    Only authenticated users who are participants in the conversation can perform this action.
    """
    permission_classes = [IsAuthenticated, IsParticipantInConversation]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversations, pk=conversation_id)
        user = request.user

        self.check_object_permissions(request, conversation)
        if user == conversation.player1:
            conversation.IsVisibleToPlayer1 = False
            Messages.objects.filter(atConversation=conversation).update(
                IsVisibleToPlayer1=False)
        else:
            Messages.objects.filter(atConversation=conversation).update(
                IsVisibleToPlayer2=False)
            conversation.IsVisibleToPlayer2 = False

        conversation.save(
            update_fields=['IsVisibleToPlayer1', 'IsVisibleToPlayer2'])

        # If the conversation is not visible to both players, delete it
        if not conversation.IsVisibleToPlayer1 and not conversation.IsVisibleToPlayer2:
            conversation.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing friendships between players.

    This ViewSet provides the following actions:
    - `list`: Get a list of all friendships.
    - `create`: Create a new friendship request.
    - `retrieve`: Get details of a specific friendship.
    - `destroy`: Delete a specific friendship.
    - `accept_friendship`: Accept a friendship request.
    - `reject_friendship`: Reject a friendship request.
    """

    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get the queryset of friendships.

        Returns:
            QuerySet: The queryset of friendships.
        """
        user = self.request.user
        return Friendship.objects.filter(models.Q(player1=user) | models.Q(player2=user))

    def perform_create(self, serializer):
        """
        Perform creation of a new friendship request.

        Args:
            serializer (FriendshipSerializer): The serializer instance.

        Raises:
            serializers.ValidationError: If player2 is not provided, or if the friendship request is a duplicate,
                or if a friendship already exists between the players, or if the player tries to send a friend request to themselves.
        """
        user = self.request.user
        player2_username = self.request.data.get('player2_username')

        if not player2_username:
            raise serializers.ValidationError(
                'player2 is required to create a friend request.')

        player2 = Player.objects.get(username=player2_username)

        # Prevent self-friending
        if player2 == user:
            raise serializers.ValidationError(
                'You cannot send a friend request to yourself.')

        # Prevent duplicate friendship requests
        if Friendship.objects.filter(player1=user, player2=player2, friendshipAccepted=False).exists():
            raise serializers.ValidationError(
                'A pending friendship request already exists.')

        # Prevent duplicate friendships
        if Friendship.objects.filter(models.Q(player1=user, player2=player2) | models.Q(player1=player2, player2=user)).exists():
            raise serializers.ValidationError(
                'A friendship already exists between these players.')

        # Create a new friendship request
        serializer.save(player1=user, player2=player2)

    @action(detail=True, methods=['patch'], url_path='accept')
    def accept_friendship(self, request, pk=None):
        """
        Accept a friendship request.

        Args:
            request (Request): The request object.
            pk (int): The primary key of the friendship.

        Returns:
            Response: The response indicating the success or failure of the operation.
        """
        friendship = self.get_object()
        if friendship.player2 == request.user:
            friendship.friendshipAccepted = True
            friendship.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['patch'], url_path='reject')
    def reject_friendship(self, request, pk=None):
        """
        Reject a friendship request.

        Args:
            request (Request): The request object.
            pk (int): The primary key of the friendship.

        Returns:
            Response: The response indicating the success or failure of the operation.
        """
        friendship = self.get_object()
        if friendship.player2 == request.user:
            friendship.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
