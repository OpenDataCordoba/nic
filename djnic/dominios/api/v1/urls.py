from django.urls import path, include
from rest_framework import routers
from .views import DominioViewSet, NextPriorityDomainViewSet


router = routers.DefaultRouter()
router.register(r'dominio', DominioViewSet)
router.register(r'next-priority', NextPriorityDomainViewSet, basename='next-priority')

urlpatterns = [
    path('stats/', include('dominios.api.v1.urls_stats')),
    path('', include(router.urls)),
]
