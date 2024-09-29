from .views import *
from django.urls import path, include

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('me/', PlayerProfileView.as_view(), name='me'),
    path('register/', RegisterView.as_view(), name='register'),
    path('players/', PlayerListView.as_view(), name='player_list'),
    path('profile/<str:username>/',
        PlayerPublicProfileView.as_view(), name='player_profile'),
    path('login/', LoginView.as_view(), name='login'),
 
	  path('setup-2fa/', SetupTwoFactorView.as_view(), name='setup_2fa'),
	  path('verify-2fa/', VerifyTwoFactorView.as_view(), name='verify_2fa'),
  	path('disable-2fa/', DisableTwoFactorView.as_view(), name='disable_2fa'),
	  path('use-backup-code/', UseBackupCodeView.as_view(), name='use_backup_code'),

    path('logout/', LogoutView.as_view(), name='logout'),
    path('update-info/', UpdatePlayerInfoView.as_view(), name='update_player'),
    path('update-password/', ChangePasswordView.as_view(), name='update_password'),
    path('update-avatar/', UpdateAvatarView.as_view(), name='avatar'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('oauth/login/', OAuthLoginView.as_view(), name='oauth_login'),
    path('oauth/callback/', OAuthCallbackView.as_view(), name='oauth_callback'),
]
