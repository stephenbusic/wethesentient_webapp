from django.urls import path
from .views import *

app_name = 'follow'

urlpatterns = [
    path('request-subscription', request_sub, name="request_sub"),
    path('confirm-subscription', sub_confirmation, name='sub_confirmation'),
    path('unsubscribe', unsub_confirmation, name='unsub_confirmation'),
]