from django.urls import path, include


urlpatterns = [
    path('v1/dominios/', include('dominios.api.v1.urls')),
    path('v1/registrantes/', include('registrantes.api.v1.urls')),
    path('v1/cambios/', include('cambios.api.v1.urls')),
    path('v1/zonas/', include('zonas.api.v1.urls')),
]
