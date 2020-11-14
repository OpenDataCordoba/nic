from django.urls import path, include
from rest_framework import routers
from .views import (DominioViewSet, NextPriorityDomainViewSet, 
                    UltimosCaidosViewSet, UltimosRenovadosViewSet,
                    UltimosTranspasadosViewSet, UltimosCambioDNSViewSet)


router = routers.DefaultRouter()
router.register(r'dominio', DominioViewSet, basename='dominio')
router.register(r'next-priority', NextPriorityDomainViewSet, basename='next-priority')
router.register(r'ultimos-caidos', UltimosCaidosViewSet, basename='ultimos-caidos')
router.register(r'ultimos-renovados', UltimosRenovadosViewSet, basename='ultimos-renovados')
router.register(r'ultimos-transpasados', UltimosTranspasadosViewSet, basename='ultimos-transpasados')
router.register(r'ultimos-cambio-dns', UltimosCambioDNSViewSet, basename='ultimos-cambio-dns')

urlpatterns = [
    path('stats/', include('dominios.api.v1.urls_stats')),
    path('', include(router.urls)),
]
