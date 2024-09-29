import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import pyotp


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
    online = models.BooleanField(default=False)

    # Using unique related names for groups and user_permissions to avoid conflicts with ORM.
    groups = models.ManyToManyField(
        Group, related_name='player_groups', blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name='player_user_permissions', blank=True)
    
    # 2FA fields
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    
    def generate_two_factor_secret(self):
        """
		Generate a 2FA secret for the player.
		"""
        return pyotp.random_base32()
    
    def get_totp(self):
        """
        Generates a TOTP object using the player's two-factor secret.
        """
        return pyotp.TOTP(self.two_factor_secret)
    
    def verify_two_factor_code(self, code):
        """
		Verify a 2FA code.
		"""
        totp = self.get_totp()
        return totp.verify(code)
    
    def generate_backup_codes(self, count=5):
        """
		Generate backup codes for the player.
        """
        return [pyotp.random_base32()[:8] for _ in range(count)]
    
    def use_backup_code(self, code):
        """
		Used to verify a 2FA code when the player does not have access to their 2FA device.
        """
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False
