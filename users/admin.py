from django.contrib import admin
from .models import Profile





@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Профили пользователей"""
    list_display = ('username', 'email', 'about', 'image')