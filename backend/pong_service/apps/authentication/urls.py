import pong_service.apps.authentication.views as views
from django.urls import path

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('players/', views.PlayerListView.as_view(), name='player_list'),
    path('profile/<str:username>/', views.PlayerPublicProfileView.as_view(), name='player_profile'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('oauth/login/', views.OAuthLoginView.as_view(), name='oauth_login'),
    path('oauth/callback/', views.OAuthCallbackView.as_view(), name='oauth_callback'),
]
