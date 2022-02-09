from django.db import models
from django.contrib.auth.models import AbstractUser

# User Info

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    
    avatar = models.ImageField(null=True, default="avatar.svg")
    
    is_email_verified = models.BooleanField(default=False)

    #leagues =
    wons = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False, verbose_name="Is Online")
    xp = models.IntegerField(default=10, verbose_name="XP")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

