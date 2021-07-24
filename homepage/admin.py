from django.contrib import admin
from homepage.models import Subscriber


class SubscriberAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created',)
    list_display = ['email', 'date_created']


admin.site.register(Subscriber, SubscriberAdmin)



