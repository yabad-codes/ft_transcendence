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
         MessageListCreateAPI.as_view(), name='message_list_create'),
    path('conversations/<int:conversation_id>/clear',
         ConversationClearView.as_view(), name='conversation_clear'),
    path('conversations/<int:conversation_id>/delete',
    ConversationDeleteView.as_view(), name='conversation_clear'),
]
