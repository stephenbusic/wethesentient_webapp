from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

class MyUserAdmin(admin.ModelAdmin):

    list_display = ['username', 'email', 'date_joined']

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

admin.site.unregister(Site)
#admin.site.unregister(Group)
