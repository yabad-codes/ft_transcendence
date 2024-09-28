import re
from .models import Player
from rest_framework.exceptions import ValidationError
from django.core.validators import RegexValidator 
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from PIL import Image

USERNAME_REGEX = r'^(?=[a-zA-Z0-9]*-?[a-zA-Z0-9]*$)[a-zA-Z][a-zA-Z0-9\-]{2,19}$'
NAME_REGEX = r'^[a-zA-Z]+([ -][a-zA-Z]+)*$'

USERNAME_ERROR = "Username: 3-20 chars, 1+ letter, no spaces, only letters, numbers, or _."
NAME_ERROR = "First and last name must contain only letters, or a single space or hyphen followed by a letter."

INCLUDE_USERNAME_AND_PASSWORD = "Must include 'username' and 'password'."
INVALID_USERNAME_OR_PASSWORD = "Invalid username or password."

def password_validator(password):
    """
    Validates the strength of a password.

    Args:
            password (str): The password to be validated.

    Raises:
            ValidationError: If the password does not meet the required criteria.

    Returns:
            None
    """

    validate_password(password)
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            'Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            'Password must contain at least one lowercase letter.')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one digit.')
    if not re.search(r'[\W_]', password):
        raise ValidationError(
            'Password must contain at least one special character.')

def username_validator(username):
    """
    Validates the given username.

    Checks if the username already exists in the database and raises a ValueError if it does.
    Additionally, applies a regex validation to ensure the username matches a specific pattern.

    Args:
            username (str): The username to be validated.

    Raises:
            ValueError: If the username already exists in the database.

    Returns:
            None
    """
    
    if Player.objects.filter(username=username).exists():
        raise ValidationError('Username already exists.')
    regex_validator = RegexValidator(
        regex=USERNAME_REGEX,
        message=USERNAME_ERROR
    )
    regex_validator(username)
    
def tournament_name_validator(nickname):
    """
    Validates the given username.

    Checks if the username already exists in the database and raises a ValueError if it does.
    Additionally, applies a regex validation to ensure the username matches a specific pattern.

    Args:
            username (str): The username to be validated.

    Raises:
            ValueError: If the username already exists in the database.

    Returns:
            None
    """
    
    if Player.objects.filter(tournament_name=nickname).exists():
        raise ValidationError('Nickname already exists.')
    regex_validator = RegexValidator(
        regex=USERNAME_REGEX,
        message=USERNAME_ERROR
    )
    regex_validator(nickname)

def name_validator(name):
    """
    Validates the given name using a regex pattern.

    Args:
            name (str): The name to be validated.

    Raises:
            ValidationError: If the name does not match the regex pattern.

    Returns:
            None
    """

    regex_validator = RegexValidator(
        regex=NAME_REGEX,
        message=NAME_ERROR
    )
    regex_validator(name)

def validate_login_data(username, password):
    """
    Validates the login data by checking if the username and password are provided,
    and authenticates the user using the provided credentials.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        User: The authenticated user.

    Raises:
        serializers.ValidationError: If the username or password is invalid or not provided.
    """

    if username and password:
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(INVALID_USERNAME_OR_PASSWORD)
    else:
        raise serializers.ValidationError(INCLUDE_USERNAME_AND_PASSWORD)
    return user

def validate_avatar(value):
    """
    Validates the avatar image file.

    Parameters:
    value (file): The avatar image file to be validated.

    Returns:
    file: The validated avatar image file.

    Raises:
    ValidationError: If the image format is not supported or if the image is invalid.
    """
    try:
        img = Image.open(value)
        img.verify()
        if img.format.lower() not in ['png', 'jpeg', 'jpg', 'gif']:
            raise ValidationError("Image format not supported")
        value.seek(0)
    except Exception as e:
        raise ValidationError("Invalid image")
    return value