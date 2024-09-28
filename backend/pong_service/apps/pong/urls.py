from django.urls import path
from . import views as views

urlpatterns = [
	path('play/request-game/', views.RequestGameView.as_view(), name='request_game'),
]