from django.contrib.sitemaps import Sitemap


class HomePageSitemap(Sitemap):

    def items(self):
        return [self]

    location = '/'
    changefreq = 'monthly'
    priority = '1'
