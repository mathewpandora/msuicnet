from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    favorite_genres = models.CharField(max_length=255, null=True, blank=True)
    vk = models.CharField(max_length=255, null=True, blank=True)
    tg = models.CharField(max_length=255, null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

