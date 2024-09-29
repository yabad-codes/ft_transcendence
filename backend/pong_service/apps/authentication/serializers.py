from django.core.validators import RegexValidator
from rest_framework import serializers
from .models import Player
from pong_service.apps.chat.models import Friendship
import pong_service.apps.authentication.validators as validators
import pong_service.apps.authentication.helpers as helpers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q

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
                  'password', 'password_confirm')

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
            print(PASSWORD_ERROR)
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
            return helpers.create_player(validated_data)
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
        return helpers.get_player_representation(instance)


class PlayerListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Player model used in the player list view.
    """

    isFriend = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ('username', 'first_name',
                  'last_name', 'avatar_url', 'wins', 'losses', 'isFriend', 'online')

    def get_isFriend(self, obj):
        """
        Gets the isFriend field for the player.

        Args:
            obj (Player): The player object.

        Returns:
            bool: True if the player is a friend, False otherwise.
        """
        user = self.context['request'].user
        return Friendship.objects.filter(
            (Q(player1=user) & Q(player2=obj) & Q(friendshipAccepted=True)) |
            (Q(player1=obj) & Q(player2=user) & Q(friendshipAccepted=True))
        ).exists()

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

class UpdatePlayerInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for updating player information.
    """
    
    username = serializers.CharField(
        required=False,
        max_length=30,
        validators=[validators.username_validator]
    )

    first_name = serializers.CharField(
        required=False,
        max_length=30,
        validators=[validators.name_validator]
    )

    last_name = serializers.CharField(
        required=False,
        max_length=30,
        validators=[validators.name_validator]

    )

    class Meta:
        model = Player
        fields = ('username', 'first_name', 'last_name')
    
    def validate(self, data):
        """
        Validates the input data.

        Args:
            data (dict): The input data to be validated.

        Returns:
            dict: The sanitized and validated data.
        """
        sanitized_data = helpers.sanitize_and_validate_data(data)
        return sanitized_data

    def update(self, instance, validated_data):
        """
        Update method for the serializer.

        Args:
            instance: The instance of the object to be updated.
            validated_data: The validated data to update the instance with.

        Returns:
            The updated instance.

        Raises:
            serializers.ValidationError: If an error occurs during the update process.
        """
        return helpers.update_player_info(self, instance, validated_data)

class UpdateAvatarSerializers(serializers.ModelSerializer):
    """
    Serializer for updating the avatar of a Player instance.
    """

    avatar = serializers.ImageField(required=False)
    
    class Meta:
        model = Player
        fields = ['avatar', 'avatar_url']
        read_only_fields = ['avatar_url']
    
    def validate_avatar(self, value):
        """
        Validates the avatar .

        Args:
            value: The avatar  to be validated.

        Returns:
            The validated avatar .

        Raises:
            ValidationError: If the avatar  is invalid.
        """
        return validators.validate_avatar(value)
    
    def update(self, instance, validated_data):
        """
        Updates the instance with the validated data.

        Args:
            instance: The instance to be updated.
            validated_data: The validated data to update the instance with.

        Returns:
            The updated instance.
        """
        avatar = validated_data.get('avatar')
        if avatar:
            url = helpers.upload_to_google_cloud(avatar, instance)
          
            instance.avatar_url = url
            instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer class for changing password.
    """

    old_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validators.password_validator]
    )
    
    confirm_new_password = serializers.CharField(
        write_only=True,
        required=True
    )
    def validate_old_password(self, value):
        """
        Validate the old password.

        Args:
            value (str): The old password to be validated.

        Returns:
            str: The validated old password.

        Raises:
            serializers.ValidationError: If the old password is incorrect.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        return value
    
    def validate(self, data):
        """
        Validate the input data.

        Args:
            data (dict): The input data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the new password and its confirmation do not match.
        """
        if data['new_password'] != data['confirm_new_password']:
                raise serializers.ValidationError(PASSWORD_ERROR)
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError("New password cannot be the same as the old password.")
        return data
    
    def update(self, instance, validated_data):
        return helpers.update_password(self, instance, validated_data)


class CreatePasswordSerializer(serializers.ModelSerializer):
    """
    Serializer class for creating a password.

    This serializer is used to create a new password for a user.

    Attributes:
        password (CharField): The password field.
        password_confirm (CharField): The password confirmation field.
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

    def validate(self, validated_data):
        """
        Validates the validated_data provided in the serializer.

        Args:
            validated_data (dict): The validated_data to be validated.

        Returns:
            dict: The validated validated_data.

        Raises:
            serializers.ValidationError: If the password and password_confirm fields do not match.
        """
        if validated_data['password'] != validated_data['password_confirm']:
            raise serializers.ValidationError(PASSWORD_ERROR)
        return validated_data
    
    def create(self, instance, validated_data):
        """
        Create a new instance of the serializer's associated model.

        Args:
            instance: The instance of the serializer's associated model.
            validated_data: The validated data for creating the instance.

        Returns:
            The created instance of the serializer's associated model.
        """
        validated_data.pop('password_confirm')
        password = validated_data['password']
        instance.set_password(password)
        instance.save()
        return instance
    