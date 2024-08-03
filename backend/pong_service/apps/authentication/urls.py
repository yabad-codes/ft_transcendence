from .views import *
from django.urls import path

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('players/', PlayerListView.as_view(), name='player_list'),
    path('profile/<str:username>/',
         PlayerPublicProfileView.as_view(), name='player_profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', CustomTokenRefreshView.as_view(), name='jwt-refresh'),
]
