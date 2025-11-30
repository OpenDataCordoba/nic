import logging
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializer import FullCambiosDominioSerializer, FullCampoCambioSerializer
from cambios.models import CambiosDominio, CampoCambio
from cache_memoize import cache_memoize
from django.conf import settings

logger = logging.getLogger(__name__)


class CambiosDominioViewSet(viewsets.ModelViewSet):
    serializer_class = FullCambiosDominioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['-id']

    MAX_QUERYSET_SIZE = 1000

    @cache_memoize(settings.GENERAL_CACHE_SECONDS)
    def get_queryset(self):
        return CambiosDominio.objects.all()[:self.MAX_QUERYSET_SIZE]


class CampoCambioViewSet(viewsets.ModelViewSet):
    serializer_class = FullCampoCambioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['campo', 'anterior', 'nuevo']
    ordering_fields = '__all__'
    ordering = ['-id']

    MAX_QUERYSET_SIZE = 1000

    @cache_memoize(settings.GENERAL_CACHE_SECONDS)
    def get_queryset(self):
        # Use cached queryset, ignoring user/token
        return CampoCambio.objects.all()[:self.MAX_QUERYSET_SIZE]