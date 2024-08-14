from .views import *
from django.urls import path, include

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('register/', RegisterView.as_view(), name='register'),
    path('players/', PlayerListView.as_view(), name='player_list'),
    path('profile/<str:username>/',
         PlayerPublicProfileView.as_view(), name='player_profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
