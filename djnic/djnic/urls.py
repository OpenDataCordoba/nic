from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('djnic.api.urls')),
    path('api-token-auth/', views.obtain_auth_token),
    path('', include('web.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
