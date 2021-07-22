from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from homepage.models import Subscriber

User = get_user_model()


class MyUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'date_joined']


admin.site.register(Subscriber)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.unregister(Site)



