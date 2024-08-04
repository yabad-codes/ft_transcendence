from google.cloud import storage
from django.conf import settings
import uuid
from django.core.validators import RegexValidator
from rest_framework import serializers
from .models import Player
import pong_service.apps.authentication.validators as validators
import pong_service.apps.authentication.helpers as helpers
from django.contrib.auth.password_validation import validate_password


# Error messages
GENERAL_ERROR = "An error occurred. Please try again."
PASSWORD_ERROR = "Passwords do not match."
USERNAME_FORMAT_ERROR = "Invalid username format."

import logging
logger = logging.getLogger(__name__)
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


class UpdatePlayerInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for updating player information.

    Attributes:
        username (CharField): The username field.
        first_name (CharField): The first name field.
        last_name (CharField): The last name field.

    Meta:
        model (Player): The model to be serialized.
        fields (tuple): The fields to be included in the serialized representation.

    Methods:
        validate(data): Validates the input data.
        update(instance, validated_data): Updates the instance with the validated data.
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
    


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer class for changing password.

    Attributes:
        old_password (CharField): The old password field.
        new_password (CharField): The new password field.
        confirm_new_password (CharField): The confirm new password field.
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
        return data
    
    def update(self, instance, validated_data):
        return helpers.update_password(self, instance, validated_data)
    

def upload_to_google_cloud(image):
    client = storage.Client(credentials=settings.GS_CREDENTIALS, project=settings.GS_PROJECT_ID)
    bucket = client.bucket(settings.GS_BUCKET_NAME)
    blob_name = f"avatars/{uuid.uuid4()}{image.name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_file(image, content_type=image.content_type)
    return blob.public_url 

class UpdateAvatarSerializers(serializers.ModelSerializer):
    avatar_url = serializers.ImageField(required=False)
    
    class Meta:
        model = Player
        fields=['avatar_url','avatar']
        read_only_fields=['avatar']
    
    def update(self, instance, validated_data):
        avatar_url = validated_data.get('avatar_url')
        if avatar_url:
            url = upload_to_google_cloud(avatar_url)
            logger.debug(f"Avatar URL: {url}")
            instance.avatar = url
            instance.save()
        return instance
            
        
        
