from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'bio', 'favorite_genres', 'vk', 'tg', 'followers']
        read_only_fields = ['followers']
