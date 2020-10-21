from django.urls import path, include
from rest_framework import routers
from .views import ZonaViewSet


router = routers.DefaultRouter()
router.register(r'zona', ZonaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
