from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # фотография профиля
    bio = models.TextField(null=True, blank=True)  # короткое описание пользователя
    favorite_genres = models.CharField(max_length=255, null=True, blank=True)  # предпочтительные музыкальные стили
    # дополнительные поля для соцсетей
    vk = models.CharField(max_length=255, null=True, blank=True)
    tg = models.CharField(max_length=255, null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False)

    def __str__(self):
        return self.username

