import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class Player(AbstractUser):
    """
    Represents a player in the system.
    """
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    api_user_id = models.IntegerField(blank=True, null=True, unique=True)
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    tournament_name = models.CharField(
        max_length=30, blank=True, unique=True, null=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    # Using unique related names for groups and user_permissions to avoid conflicts with ORM.
    groups = models.ManyToManyField(
        Group, related_name='player_groups', blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name='player_user_permissions', blank=True)
