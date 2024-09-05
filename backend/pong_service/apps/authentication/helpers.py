import bleach
from rest_framework import serializers
from .models import Player
from django.conf import settings


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
		avatar=validated_data.get('avatar', None)
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

def set_cookie(response, key, value, max_age):
    """
    Set a cookie in the response object.
    
    Args:
		response (Response): The response object.
		key (str): The cookie key.
		value (str): The cookie value.
		max_age (int): The cookie's max age in seconds.
  
    Returns:
		Response: The response object with the cookie set.
    """
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH
    )
    return response