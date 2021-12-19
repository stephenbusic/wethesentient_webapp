from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site
from django.urls import reverse
from urllib.parse import urljoin

from posts.models import AGPost

class AGPostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return AGPost.objects.filter(unlisted=False)

    def lastmod(self, obj):
        return obj.date
