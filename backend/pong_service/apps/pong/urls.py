from django.urls import path
from . import views as views

urlpatterns = [
	path('play/request-game/', views.RequestGameView.as_view(), name='request_game'),
 	path('play/request-game-with-player/', views.RequestGameWithPlayerView.as_view(), name='request_game_with_player'),
    path('play/accept-game-request/', views.AcceptGameRequestView.as_view(), name='accept_game_request'),
    path('history/matches/<str:username>/', views.PlayerGamesView.as_view(), name='player_matches'),
]