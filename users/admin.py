from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Group
from allauth.account.models import EmailAddress


# Customize the display and change forms for User
class UserAdmin(UserAdmin):
    filter_horizontal = ('groups', 'user_permissions')

    def users_comments(self):
        return mark_safe('<a href="/admin/posts/comment/?author__id__exact=%d">%s</a>' % (self.id, self.username + '\'s comments'))

    def users_replies(self):
        return mark_safe('<a href="/admin/posts/reply/?author__id__exact=%d">%s</a>' % (self.id, self.username+ '\'s replies'))

    list_display = ['username', 'first_name', 'email', users_comments, users_replies]


# Re-register UserAdmin to apply changes
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Unregister unneeded models
admin.site.unregister(EmailAddress)
admin.site.unregister(Group)


