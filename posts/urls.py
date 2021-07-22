from django.urls import path
from .views import allposts, show_post

app_name = 'posts'

urlpatterns = [
    path('show/<int:page_num>', allposts, name="show_all_posts"),
    path('<slug:slug>', show_post, name="show")
]