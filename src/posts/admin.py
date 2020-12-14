from django.contrib import admin
from .models import AGPost, Comment, Reply

admin.site.register(AGPost)
admin.site.register(Comment)
admin.site.register(Reply)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)