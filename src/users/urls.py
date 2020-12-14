from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    # Unnotify for a users comments and replies
    path('disable-comment-notifcations', unnotify_comment_confirmation, name='unnotify_comment_confirmation'),
    path('disable-reply-notifcations', unnotify_reply_confirmation, name='unnotify_reply_confirmation'),
]
