from django.urls import path, include


urlpatterns = [
    path('v1/dominios/', include('dominios.api.v1.urls')),
    path('v1/zonas/', include('zonas.api.v1.urls')),
]
