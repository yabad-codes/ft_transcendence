from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Player(AbstractUser):
    # Additional field to store the player's avatar image
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # The groups field creates a many-to-many relationship between the Player and Group models.
    # A player can belong to multiple groups, and a group can have multiple players.
    # This is why ManyToManyField is used here.
    # Additionally, specifying a unique related_name ('player_groups') prevents conflicts
    # with the default auth.User model's reverse accessor for groups.
    groups = models.ManyToManyField(Group, related_name='player_groups', blank=True)

    # The user_permissions field creates a many-to-many relationship between the Player and Permission models.
    # A player can have multiple permissions, and a permission can be assigned to multiple players.
    # This justifies the use of ManyToManyField.
    # Specifying a unique related_name ('player_user_permissions') avoids conflicts with the
    # default auth.User model's reverse accessor for user_permissions.
    user_permissions = models.ManyToManyField(Permission, related_name='player_user_permissions', blank=True)

