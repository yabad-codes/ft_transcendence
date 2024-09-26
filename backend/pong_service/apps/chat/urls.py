from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

conversation_list = ConversationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

conversation_detail = ConversationViewSet.as_view({
    'get': 'retrieve'
})

friendship_list = FriendshipViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

friendship_detail = FriendshipViewSet.as_view({
    'get': 'retrieve',
	'delete': 'destroy'
})

accept_friendship = FriendshipViewSet.as_view({
    'patch': 'accept_friendship'
})

reject_friendship = FriendshipViewSet.as_view({
    'patch': 'reject_friendship'
})

message_list_create = MessageViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

message_detail = MessageViewSet.as_view({
    'get': 'retrieve'
})

message_mark_as_read = MessageViewSet.as_view({
    'patch': 'mark_as_read'
})

list_blocked_users = BlockedUsersViewSet.as_view({
    'get': 'list',
})

block_user = BlockedUsersViewSet.as_view({
    'patch': 'block_user',
})

unblock_user = BlockedUsersViewSet.as_view({
    'delete': 'unblock_user',
})

urlpatterns = [
    path('friendships/', friendship_list, name='friendship-list-create'),
    path('friendships/<int:pk>/', friendship_detail, name='friendship-detail'),
    path('friendships/<int:pk>/accept/',
         accept_friendship, name='friendship-accept'),
    path('friendships/<int:pk>/reject/',
         reject_friendship, name='friendship-reject'),
    path('conversations/', conversation_list,
         name='conversation_list'),
    path('conversations/<int:pk>/', conversation_detail,
         name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages',
         message_list_create, name='message_list_create'),
    path('conversations/<int:conversation_id>/messages/<int:pk>', message_detail, name='message_detail'),
    path('conversations/<int:conversation_id>/messages/<int:pk>/mark_as_read/',
         message_mark_as_read, name='message_mark_as_read'),
    path('conversations/<int:conversation_id>/clear',
         ConversationClearView.as_view(), name='conversation_clear'),
    path('conversations/<int:conversation_id>/delete',
    ConversationDeleteView.as_view(), name='conversation_clear'),
    path('profile/<str:username>/block', block_user, name='block_user'),
    path('profile/<str:username>/unblock', unblock_user, name='unblock_user'),
    path('blocked/', list_blocked_users, name='list_blocked_users'),
]
