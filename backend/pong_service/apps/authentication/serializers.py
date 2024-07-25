from io import BytesIO
import requests
import bleach
from PIL import Image
from django.core.files.base import ContentFile
from django.core import validators
from django.core.validators import RegexValidator
from django.core.files import File
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Player
from  django.contrib.auth.password_validation import validate_password

# Constants
USERNAME_REGEX = r'^(?=.*[a-zA-Z])(?=\S+$)[a-zA-Z0-9_]{3,20}$'
USERNAME_MESSAGE = 'Username must be 3-20 characters long, contain at least one letter, no spaces, and only alphanumeric characters and underscores.'
PASSWORD_MISMATCH_MESSAGE = "Password fields didn't match."
ROBOHASH_ERROR = "Failed to generate avatar from Robohash."
GENERAL_ERROR_MESSAGE = "An error occurred during registration. Please try again."
INVALID_IMAGE_ERROR = "Invalid image. Please provide a valid JPEG  or PNG image."

def generate_robohash_avatar(username):
    """
    Generates an avatar image using the Robohash service.
    """

    robohash_url = f"https://robohash.org/{username}.png"
    try:
        response = requests.get(robohash_url, timeout=10)
        response.raise_for_status()
        return File(BytesIO(response.content), name=f"{username}.png")
    except requests.RequestException:
        raise serializers.ValidationError(ROBOHASH_ERROR)
    
def validate_passwords_match(password, password_confirm):

    """
    Validate that passwords match.
    """
    if password != password_confirm:
        raise serializers.ValidationError(PASSWORD_MISMATCH_MESSAGE)

def process_avatar(avatar,username):
    """
    Process and validate the avatar image.
    """
    try:
        img = Image.open(avatar)
        
        if img.format not in ['JPEG', 'PNG', 'JPG']:
            raise ValueError(INVALID_IMAGE_ERROR)
        

        output = BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)

        filename = f"{username}.jpg"
        
        return ContentFile(output.read(), name=filename)
    except Exception as e:
        raise ValueError(f"Invalid image: {str(e)}")

def handle_avatar_upload(validated_data):
    """
    Handle avatar upload and processing.
    """

    if 'avatar' in validated_data and validated_data['avatar']:
        try:
            validated_data['avatar'] = process_avatar(validated_data['avatar'], validated_data['username'])
        except ValueError as e:
            raise serializers.ValidationError(f"Avatar error: {str(e)}")
    else:
        validated_data['avatar'] = generate_robohash_avatar(validated_data['username'])
    return validated_data

def sanitize_and_validate_data(validated_data):
    """
    Sanitize and validate the username, first_name, and last_name fields.
    """

    fields = ['username', 'first_name', 'last_name']
    for field in fields:
        validated_data[field] = bleach.clean(validated_data[field])
        validators.validate_slug(validated_data[field])
    return validated_data

def create_player(validated_data):
    """
    Create a new player with validated data.
    """
    validated_data.pop('password_confirm')
    validated_data = handle_avatar_upload(validated_data)
    validated_data = sanitize_and_validate_data(validated_data)

    return Player.objects.create_user(
        username=validated_data['username'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        password=validated_data['password'],
        avatar=validated_data.get('avatar', None)
    )

def get_player_representation(player):
    """
    Return non-sensitive player information.
    """
    return {
        'id': player.id,
        'username': player.username,
        'frist_name':player.first_name,
        'last_name':player.last_name,
        'avatar': player.avatar.url if player.avatar else None
    }

class PlayerRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for player registration.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True
    )
    username = serializers.CharField(
        required=True,
        max_length=30,
        validators=[
            UniqueValidator(queryset=Player.objects.all()),
            RegexValidator(
                regex=USERNAME_REGEX,
                message=USERNAME_MESSAGE
            ),
        ]
    )
    first_name = serializers.CharField(
        required=True,
        max_length=30
    )
    last_name = serializers.CharField(
        required=True,
        max_length=30
    )

    class Meta:
        model = Player
        fields = ('username','first_name','last_name', 'password', 'password_confirm', 'avatar')

    def validate(self, data):
        validate_passwords_match(data['password'], data['password_confirm'])
        return data

    def create(self, validated_data):
        try:
            return create_player(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"{GENERAL_ERROR_MESSAGE}: {str(e)}")
    
    def to_representation(self, instance):
        return get_player_representation(instance)

class PlayerListSerializer(serializers.ModelSerializer):
    """
    Serializer for player list.
    """

    class Meta:
        model = Player
        fields =('id','username','first_name','last_name', 'avatar','wins','losses')


class PlayerPublicProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for public player profile.
    """
    class Meta:
        model = Player
        fields =('id','username','first_name','last_name', 'avatar', 'wins', 'losses')