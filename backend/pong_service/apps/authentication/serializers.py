from django.core.validators import RegexValidator
from rest_framework import serializers
from .models import Player
import pong_service.apps.authentication.validators as validators
from pong_service.apps.authentication.helpers import create_player, get_player_representation
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Error messages
GENERAL_ERROR = "An error occurred. Please try again."
PASSWORD_ERROR = "Passwords do not match."
USERNAME_FORMAT_ERROR = "Invalid username format."


class PlayerRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for player registration.

    This serializer is used to validate and serialize player registration data.
    It includes fields for username, first name, last name, password, password confirmation, and avatar.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validators.password_validator]
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True
    )

    username = serializers.CharField(
        required=True,
        max_length=30,
        validators=[validators.username_validator]
    )

    first_name = serializers.CharField(
        required=True,
        max_length=30,
        validators=[validators.name_validator]
    )

    last_name = serializers.CharField(
        required=True,
        max_length=30,
        validators=[validators.name_validator]

    )

    class Meta:
        model = Player
        fields = ('username', 'first_name', 'last_name',
                  'password', 'password_confirm', 'avatar')

    def validate(self, data):
        """
        Validates the data provided in the serializer.

        Args:
            data (dict): The data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the password and password_confirm fields do not match.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(PASSWORD_ERROR)
        return data

    def create(self, validated_data):
        """
        Create a new player.

        Args:
            validated_data (dict): Validated data for creating the player.

        Returns:
            Player: The created player object.

        Raises:
            serializers.ValidationError: If there is an error creating the player.
        """
        try:
            return create_player(validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                f"{GENERAL_ERROR}: {str(e)}")

    def to_representation(self, instance):
        """
        Converts the given instance into a representation suitable for serialization.

        Args:
            instance: The instance to be converted.

        Returns:
            The serialized representation of the instance.
        """
        return get_player_representation(instance)


class PlayerListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Player model used in the player list view.
    """

    class Meta:
        model = Player
        fields = ('username', 'first_name',
                  'last_name', 'avatar', 'wins', 'losses')


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for user login.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    username = serializers.CharField(
        required=True,
        max_length=30,
        validators=[
            RegexValidator(
                regex=validators.USERNAME_REGEX,
                message=USERNAME_FORMAT_ERROR
            ),
        ]
    )

    class Meta:
        model = Player
        fields = ['username', 'password']

    def validate(self, data):
        """
        Validate the login data.

        Args:
            data (dict): The login data containing username and password.

        Returns:
            dict: The validated login data.

        Raises:
            ValidationError: If the login data is invalid.
        """
        username = data.get('username')
        password = data.get('password')

        user = validators.validate_login_data(username, password)
        data['user'] = user
        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
	Custom TokenObtainPairSerializer that includes the username in the token response.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token