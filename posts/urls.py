from django.urls import path
from .views import allposts, show_post, record_post_view, get_viewchart_data

app_name = 'posts'

urlpatterns = [
    path('show/<int:page_num>', allposts, name="show_all_posts"),
    path('<slug:slug>', show_post, name="show"),
    path('ajax/record-view', record_post_view, name="record_post_view"),
    path('ajax/get_view_data', get_viewchart_data, name="get_viewchart_data"),
]
