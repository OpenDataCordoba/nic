from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.authtoken import views

from .views import DominioSitemap, RegistranteSitemap, RubroSitemap, HostingSitemap

sitemaps = {
    'dominio': DominioSitemap,
    'registrante': RegistranteSitemap,
    'rubro': RubroSitemap,
    'hosting': HostingSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('djnic.api.urls')),
    path('api-token-auth/', views.obtain_auth_token),
    path('', include('web.urls')),
    path('sitemap.xml', cache_page(86400)(sitemap), {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
