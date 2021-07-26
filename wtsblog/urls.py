"""wtsblog URL Configuration"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

app_name = 'root'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('homepage.urls')),
    path('posts/', include('posts.urls')),
    path('veganism/', include('veganism.urls')),
    path('users/', include('users.urls')),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

admin.site.site_title = 'admin | WETHESENTIENT'
admin.site.index_title = ''

admin.site.index_template = 'admin/custom_admin_index.html'
admin.autodiscover()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
