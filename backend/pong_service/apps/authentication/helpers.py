import bleach
from .models import Player
from google.cloud import storage
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
		if field in validated_data:
			validated_data[field] = bleach.clean(validated_data[field])
	return validated_data

def handle_avatar(validated_data):
	"""
	Generates an avatar URL based on the provided username.

	Args:
		validated_data (dict): A dictionary containing the validated data.

	Returns:
		dict: The updated validated data dictionary with the 'avatar' field added.
    """
	username = validated_data['username']
	validated_data['avatar_url'] = f'https://robohash.org/{username}.jpg'
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
		avatar_url=validated_data.get('avatar_url', None)
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
		'avatar_url': player.avatar_url if player.avatar_url else None
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

def upload_to_google_cloud(image , instance):
	"""
	Uploads an image to Google Cloud Storage.

	Args:
		image (File): The image file to be uploaded.
		instance: The instance associated with the image.

	Returns:
		str: The public URL of the uploaded image.
	"""
	client = storage.Client(credentials=settings.GS_CREDENTIALS, project=settings.GS_PROJECT_ID)
	bucket = client.bucket(settings.GS_BUCKET_NAME)
	extension = image.name.split('.')[-1]
	blob_name = f"avatars/{instance.username}.{extension}"
	blob = bucket.blob(blob_name)
	blob.upload_from_file(image, content_type=image.content_type)
	return blob.public_url
