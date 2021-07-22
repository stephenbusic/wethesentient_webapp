from django.urls import path
from .views import veganism_index

app_name = 'veganism'

urlpatterns = [
    path('main', veganism_index, name="show_veganism_index"),
]