from .views import  *
from django.urls import path

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('players/', PlayerListView.as_view(), name='player_list'),
    path('profile/<str:username>/', PlayerPublicProfileView.as_view(), name='player_profile'),
]
