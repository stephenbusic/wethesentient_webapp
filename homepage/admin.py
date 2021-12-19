from django.contrib import admin
from homepage.models import Subscriber
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress


class SubscriberAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created',)
    list_display = ['email', 'date_created']


admin.site.register(Subscriber, SubscriberAdmin)

# Unregister unneeded models
admin.site.unregister(EmailAddress)
admin.site.unregister(Group)
# admin.site.unregister(Site)



