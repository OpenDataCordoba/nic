from django.urls import path, include
from rest_framework import routers
from .views import CambiosDominioViewSet, CampoCambioViewSet


router = routers.DefaultRouter()
router.register(r'cambio', CambiosDominioViewSet)
router.register(r'campo', CampoCambioViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
