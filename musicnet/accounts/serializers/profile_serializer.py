from rest_framework import serializers
from accounts.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'avatar', 'bio', 'favorite_genres', 'vk', 'tg', 'followers')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar', 'bio', 'favorite_genres', 'vk', 'tg')
