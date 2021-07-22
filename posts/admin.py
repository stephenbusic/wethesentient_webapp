from django.contrib import admin
from .models import AGPost, Comment, Reply

# Custom edit forms for admin page
class CommentAdmin(admin.ModelAdmin):
    fields = ('agpost', 'author', 'body', 'rank', 'notify', 'active', 'edited')
    readonly_fields = ('agpost', 'author')
    exclude = ('pinned', 'created_on', 'deactivated_on')


class ReplyAdmin(admin.ModelAdmin):
    fields = ('comment', 'author', 'body', 'rank', 'notify', 'active', 'edited')
    readonly_fields = ('comment', 'author')
    exclude = ('pinned', 'created_on', 'deactivated_on')


# Register models to admin page
admin.site.register(AGPost)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)