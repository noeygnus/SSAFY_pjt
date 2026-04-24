from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("추가 정보", {"fields": ("nickname", "interest_stocks", "profile_image")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("추가 정보", {"fields": ("nickname", "interest_stocks", "profile_image")}),
    )
    list_display = ("username", "nickname", "is_staff", "date_joined")
    search_fields = ("username", "nickname")
