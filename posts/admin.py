from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import AGPost, Comment, Reply, AGPostView


class AGPostAdmin(admin.ModelAdmin):

    def agposts_views(self):
        view_count = len(AGPostView.objects.filter(agpost=self).all())
        return mark_safe('<a href="/admin/posts/agpostview/?agpost__id__exact=%d">%s</a>' %
                         (self.id, str(view_count) + ' views'))

    list_display = ('title', 'type', 'date', agposts_views,)
    list_filter = ('type',)


class CommentAdmin(admin.ModelAdmin):
    fields = ('agpost', 'author', 'body', 'rank', 'notify', 'active', 'edited',)
    readonly_fields = ('agpost', 'author',)
    exclude = ('pinned', 'created_on', 'deactivated_on',)
    list_filter = ('author',)


class ReplyAdmin(admin.ModelAdmin):
    fields = ('comment', 'author', 'handle_user', 'body', 'rank', 'notify', 'active', 'edited',)
    readonly_fields = ('comment', 'author', 'handle_user',)
    exclude = ('pinned', 'created_on', 'deactivated_on',)
    list_filter = ('author',)


# Register models to admin page
admin.site.register(AGPost, AGPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)