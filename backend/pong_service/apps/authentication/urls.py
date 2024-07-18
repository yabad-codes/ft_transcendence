from .views import  RegisterView
from django.urls import path

"""
    This module contains the URL patterns for the authentication app.

    The urlpatterns list defines the URL patterns for the authentication app.
    - The 'register/' path is mapped to the RegisterView class-based view, which handles user registration.
    - The name 'register' is used to identify this URL pattern.
"""

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]

