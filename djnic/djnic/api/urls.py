from django.urls import path, include


urlpatterns = [
    path('v1/dominios/', include('dominios.api.v1.urls')),
]
