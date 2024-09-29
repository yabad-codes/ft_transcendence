import random
import bleach
import logging
import requests
from django.conf import settings
from rest_framework import serializers
from .models import Player
from google.cloud import storage
from django.conf import settings
from rest_framework.response import Response



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
		api_user_id=validated_data.get('api_user_id', None),
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

def set_auth_cookies(response, access_token, refresh_token):
    """
	Set the user's access and refresh tokens in the response cookies.
    """
    set_cookie(response, 'access', access_token, settings.AUTH_COOKIE_ACCESS_MAX_AGE)
    set_cookie(response, 'refresh', refresh_token, settings.AUTH_COOKIE_REFRESH_MAX_AGE)

def clear_temp_tokens(request):
    """
    Clear the temporary access and refresh tokens from the session and flush the session.
    """
    del request.session['temp_access_token']
    del request.session['temp_refresh_token']
    request.session.flush()

def error_response(message, status_code):
    """
	Create an error response with the given message and status code.
    """
    return Response({'error': message}, status=status_code)

def handle_successful_verification(request):
    """
    Handle a successful 2FA verification by setting the user's access and refresh tokens in the response cookies.

    Args:
        request (Request): The request object.

    Returns:
        Response: A response object with the user's access and refresh tokens set in the cookies.
    """
    access_token = request.session.get('temp_access_token')
    refresh_token = request.session.get('temp_refresh_token')

    if not access_token or not refresh_token:
        return error_response('Missing access or refresh token', status.HTTP_400_BAD_REQUEST)

    response = Response({'success': True})
    set_auth_cookies(response, access_token, refresh_token)
    clear_temp_tokens(request)

    return response

def get_42_token(code):
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
    api_url = 'https://api.intra.42.fr/v2/me'
    headers = {
		'Authorization': f'Bearer {access_token}'
	}
    
    response = requests.get(api_url, headers=headers)
    return response.json()

def construct_user_data(user_data):
    data = {}
    
    data['username'] = get_unique_username(user_data['login'], user_data['id'])
    data['api_user_id'] = user_data['id']
    data['first_name'] = user_data['first_name']
    data['last_name'] = user_data['last_name']
    data['password'] = None
    data['password_confirm'] = None
    data['avatar'] = user_data['image']['link']
    
    return data

def get_unique_username(username, api_user_id):
	username_exists = Player.objects.filter(username=username).exists()
	api_user_id_exists = Player.objects.filter(api_user_id=api_user_id).exists()
	
	if not api_user_id_exists and not username_exists:
		return username
	
	if not api_user_id_exists and username_exists:
		while Player.objects.filter(username=username).exists():
			username = f'{username}{random.randint(0, 100)}'
		return username

	if api_user_id_exists:
		player = Player.objects.get(api_user_id=api_user_id)
		return player.username

def user_already_exists(user_data):
    return Player.objects.filter(api_user_id=user_data['api_user_id']).exists()
