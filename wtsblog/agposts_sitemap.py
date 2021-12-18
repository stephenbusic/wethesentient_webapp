from django.contrib.sitemaps import Sitemap
from posts.models import AGPost

class AGPostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return AGPost.objects.filter(unlisted=False)

    def lastmod(self, obj):
        return obj.date
