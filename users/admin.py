from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Make permissions fully visible (might be unnecessary)
class UserAdmin(UserAdmin):
    filter_horizontal = ('groups', 'user_permissions')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
