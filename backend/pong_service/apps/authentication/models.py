from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import uuid


class Player(AbstractUser):
    """  
    Custom user model for the application.
    """
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    tournament_name = models.CharField(
        max_length=30, blank=True, unique=True, null=True)
    display_name = models.CharField(
        max_length=30, blank=True, unique=True, null=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    # Establishes many-to-many relationships with Group and Permission models, using unique related names to avoid conflicts.
    groups = models.ManyToManyField(
        Group, related_name='player_groups', blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name='player_user_permissions', blank=True)
