from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from posts.models import Comment, Reply

User = get_user_model()


# Customize the display and change forms for User
class UserAdmin(UserAdmin):
    filter_horizontal = ('groups', 'user_permissions')

    def users_comments(self):
        comment_count = len(Comment.objects.filter(author=self).all())
        return mark_safe('<a href="/admin/posts/comment/?author__id__exact=%d">%s</a>' % (self.id, str(comment_count) + ' comments'))

    def users_replies(self):
        reply_count = len(Reply.objects.filter(author=self).all())
        return mark_safe('<a href="/admin/posts/reply/?author__id__exact=%d">%s</a>' % (self.id, str(reply_count) + ' replies'))

    list_display = ['username', 'first_name', 'email', users_comments, users_replies]


# Re-register UserAdmin to apply changes
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

