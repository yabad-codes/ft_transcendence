import requests
from io import BytesIO
from django.core.files import File
from rest_framework import serializers
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import Player

# Serializer for handling player registration.
class PlayerRegistrationSerializer(serializers.ModelSerializer):
    
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
                regex='^(?=.*[a-zA-Z])[a-zA-Z0-9_]+$',
                message='Username must contain at least one letter and only contain alphanumeric characters and underscores.'
            ),
        ]
    )
 
    class Meta:
        model = Player
        fields = ('username', 'password', 'password_confirm', 'avatar')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        
        validated_data.pop('password_confirm')

        # Check if avatar is provided, if not, generate one from Robohash
        if 'avatar' not in validated_data or not validated_data['avatar']:
            # Constructing URL to fetch avatar based on username
            robohash_url = f"https://robohash.org/{validated_data['username']}.png"

            # Sending GET request to Robohash to fetch avatar
            response = requests.get(robohash_url)
             # Checking if the request to Robohash was successful
            if response.status_code == 200:
                 # Creating a File object from the response content
                avatar = File(BytesIO(response.content), name=f"{validated_data['username']}.png")
                validated_data['avatar'] = avatar

        #Creating a new Player instance with validated data
        user = Player.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            avatar=validated_data.get('avatar', None),
        )
        return user

# Serializer for listing player details.
class PlayerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields =('username', 'avatar')

 #Serializer for displaying public player profile.
class PlayerPublicProfileSerializer(serializers.ModelSerializer):
    
        class Meta:
            model = Player
            feilds =('username', 'avatar')