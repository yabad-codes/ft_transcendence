# Standard library imports
import random
import bleach
import logging
import requests

# Django library imports
from django.conf import settings

# Third-party library imports
from rest_framework import serializers

# Local application imports
from .models import Player

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def sanitize_and_validate_data(validated_data):
    """
    Sanitizes and validates the given data by cleaning specific fields using bleach.

    Args:
            validated_data (dict): The data to be sanitized and validated.

    Returns:
            dict: The sanitized and validated data.
    """
    fields = ['username', 'first_name', 'last_name']
    for field in fields:
        validated_data[field] = bleach.clean(validated_data[field])
    return validated_data


def process_avatar(avatar, username):
    """
    Process the avatar for a given username and store the image in google cloud.

    Args:
            avatar (str): The avatar image file.
            username (str): The username of the user.

    Returns:
            avatar 
    """
    print('handle google cloud storage')


def handle_avatar(validated_data):
    """
    Handle the avatar for a user.

    Args:
            validated_data (dict): The validated data containing the avatar and username.

    Returns:
            dict: The updated validated data with the avatar URL.

    Raises:
            serializers.ValidationError: If there is an error uploading the avatar to Google Cloud.
    """
    if 'avatar' in validated_data and validated_data['avatar']:
        try:
            validated_data['avatar'] = process_avatar(
                validated_data['avatar'], validated_data['username'])
        except:
            raise serializers.ValidationError(
                f"Failed to upload avatar to google cloud.")
    else:
        username = validated_data['username']
        validated_data['avatar'] = f'https://robohash.org/{username}.jpg'
    return validated_data


def create_player(validated_data):
    """
    Create a new player with the given validated data.

    Args:
            validated_data (dict): A dictionary containing the validated data for the player.

    Returns:
            Player: The newly created player object.
    """
    validated_data.pop('password_confirm')
    validated_data = handle_avatar(validated_data)
    validated_data = sanitize_and_validate_data(validated_data)

    return Player.objects.create_user(
        username=validated_data['username'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        password=validated_data['password'],
        avatar=validated_data.get('avatar', None),
        api_user_id=validated_data.get('api_user_id', None),
    )


def get_player_representation(player):
    """
    Returns a dictionary representation of a player.

    Args:
            player (Player): The player object.

    Returns:
            dict: A dictionary containing the player's username, first name, last name, and avatar URL (if available).
    """
    return {
        'username': player.username,
        'first_name': player.first_name,
        'last_name': player.last_name,
        'avatar': player.avatar if player.avatar else None
    }


def get_42_tokens(code):
    """
    Retrieves access tokens from the 42 API using the provided authorization code.

    Args:
            code (str): The authorization code obtained from the user.

    Returns:
            dict: A dictionary containing the token response in JSON format.
    """
    token_url = 'https://api.intra.42.fr/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': settings.UID,
        'client_secret': settings.SECRET,
        'redirect_uri': settings.REDIRECT_URL
    }
    token_response = requests.post(token_url, data=token_data)
    return token_response.json()


def get_42_user_data(access_token):
    """
    Retrieves user data from the 42 API using the provided access token.

    Parameters:
    access_token (str): The access token for authentication.

    Returns:
    dict: A dictionary containing the user data retrieved from the API.
    """
    api_url = 'https://api.intra.42.fr/v2/me'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(api_url, headers=headers)
    return response.json()


def get_unique_username(username):
    """
    Returns a unique username by appending a random number to the given username if it already exists in the database.

    Args:
            username (str): The username to check for uniqueness.

    Returns:
            str: A unique username.

    """
    while Player.objects.filter(username=username).exists():
        username = f'{username}{random.randint(1, 1000)}'
    return username


def construct_user_data(user_data):
    """
    Constructs a dictionary containing user data.

    Args:
            user_data (dict): A dictionary containing user data.

    Returns:
            dict: A dictionary containing the constructed user data.
    """
    data = {}

    data['username'] = get_unique_username(user_data['login'])
    data['api_user_id'] = user_data['id']
    data['first_name'] = user_data['first_name']
    data['last_name'] = user_data['last_name']
    data['password'] = None
    data['password_confirm'] = None
    data['avatar'] = user_data['image']['link']

    return data


def user_already_exists(user_data):
    """
    Check if a user already exists in the database based on the provided user data.

    Args:
        user_data (dict): A dictionary containing user data.

    Returns:
        bool: True if the user already exists, False otherwise.
    """
    if Player.objects.filter(api_user_id=user_data['api_user_id']).exists():
        return True
    return False
