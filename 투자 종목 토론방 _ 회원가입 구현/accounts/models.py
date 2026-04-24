from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    nickname = models.CharField("닉네임", max_length=50)
    interest_stocks = models.CharField("관심 종목", max_length=255, blank=True)
    profile_image = models.ImageField("프로필 이미지", upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return self.username
