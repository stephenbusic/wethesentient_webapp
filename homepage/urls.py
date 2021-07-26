from django.urls import path
from .views import *

app_name = 'homepage'

urlpatterns = [
    path('', show_homepage, name="show_homepage"),
    path('privacy-policy', show_policy, name="show_policy"),
    path('terms-of-use', show_terms, name="show_terms"),
    path('confirm-subscription', sub_confirmation, name='sub_confirmation'),
    path('unsubscribe', unsub_confirmation, name='unsub_confirmation'),
    path('ajax/get_sub_data', get_subchart_data, name="get_subchart_data"),
]