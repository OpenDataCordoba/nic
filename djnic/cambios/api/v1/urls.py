from django.urls import path, include
from rest_framework import routers
from .views import CambiosDominioViewSet, CampoCambioViewSet


router = routers.DefaultRouter()
router.register(r'cambio', CambiosDominioViewSet, basename='cambio-dominio')
router.register(r'campo', CampoCambioViewSet, basename='campo-cambio-dominio')


urlpatterns = [
    path('', include(router.urls)),
]
