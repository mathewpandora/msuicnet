from dotenv import load_dotenv
from accounts.services.email_service import send_verification_email
from rest_framework import serializers
from accounts.models import User

load_dotenv()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def send_verification_email(self, user):
        send_verification_email(user)
