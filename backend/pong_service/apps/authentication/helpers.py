import bleach
from rest_framework import serializers
from .models import Player

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
		if field in validated_data:
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
 
def update_player_info(self, instance, validated_data):
	"""
	Update the player's information with the provided validated data.

	Args:
		instance: The player instance to be updated.
		validated_data: A dictionary containing the validated data.

	Returns:
		The updated player instance.
	"""
	fields = ['username', 'first_name', 'last_name']
	for field in fields:
		if field in validated_data:
			setattr(instance, field, validated_data[field])
	instance.save()
	return instance
	
def update_password(self, instance, validated_data):
	"""
	Update the password for the given instance.

	Args:
		instance: The instance of the user model.
		validated_data: The validated data containing the new password.

	Returns:
		The updated instance with the new password.
	"""
	if 'new_password' in validated_data and 'confirm_new_password' in validated_data:
		instance.set_password(validated_data['new_password'])
		instance.save()
	return instance
