from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    # Unnotify for a users comments and replies
    path('disable-response-notifications', unnotify_confirmation, name='unnotify_confirmation'),

    # Handle user requests to delete account
    path('request-deletion', request_deletion, name='request_deletion'),
    path('confirm-deletion', deletion_confirmation, name='deletion_confirmation'),
]
