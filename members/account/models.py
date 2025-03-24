from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(
        max_length=15, unique=True,
        error_messages={"unique": "이미 사용중인 닉네임"}
    )
    profile_pic = models.ImageField(
        upload_to="profile_pics/",
        default="default_profile_pic.jpg",
        blank=True
    )
    intro = models.CharField(max_length=60, blank=True)
    email = models.EmailField(
        max_length=255, unique=True,
        error_messages={"unique": "이미 사용중인 이메일"}
    )