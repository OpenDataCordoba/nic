from django.contrib.sitemaps import Sitemap
from dominios.models import Dominio
from registrantes.models import Registrante, TagForRegistrante
from dnss.models import Empresa, DNS


class DominioSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.5
    protocol = 'https'
    limit = 3000

    def items(self):
        return Dominio.objects.all()

    def lastmod(self, obj):
        return obj.data_updated


class RegistranteSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.6
    protocol = 'https'
    limit = 3000

    def items(self):
        return Registrante.objects.all()

    def lastmod(self, obj):
        return obj.object_modified


class RubroSitemap(Sitemap):
    changefreq = "never"
    priority = 0.7
    protocol = 'https'
    limit = 3000

    def items(self):
        return TagForRegistrante.objects.all()

    def lastmod(self, obj):
        return obj.object_modified


class HostingSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.8
    protocol = 'https'
    limit = 3000

    def items(self):
        return Empresa.objects.all()

    def lastmod(self, obj):
        return obj.object_modified


class DNSSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.4
    protocol = 'https'
    limit = 3000

    def items(self):
        return DNS.objects.all()

    def lastmod(self, obj):
        return obj.object_modified
