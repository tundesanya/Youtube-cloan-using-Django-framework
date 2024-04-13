'''
Ziming: This file makes sure our own User model and its fields is accessible in Django's admin panel
'''

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.contrib.auth import get_user_model

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    # current, extra fields such as bio are not visible in /admin
    # we need to add more details here to make them visible
    pass 

admin.site.register(User, UserAdmin)