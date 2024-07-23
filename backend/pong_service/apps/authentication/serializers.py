from io import BytesIO
import requests
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
    

def create_player(validated_data):
    """
    Create a new player with validated data.
    """

    validated_data.pop('password_confirm')
    if 'avatar' not in validated_data or not validated_data['avatar']:
        validated_data['avatar'] = generate_robohash_avatar(validated_data['username'])
    
    return Player.objects.create_user(
        username=validated_data['username'],
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

    class Meta:
        model = Player
        fields = ('username', 'password', 'password_confirm', 'avatar')

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
        fields =('id','username', 'avatar')

 
class PlayerPublicProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for public player profile.
    """
    class Meta:
        model = Player
        feilds =('id','username', 'avatar')

