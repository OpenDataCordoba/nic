from datetime import timedelta
import json
import logging
import random
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache, cache_control
from rest_framework import filters
from rest_framework.decorators import action
from .serializer import CambiosDominioSerializer, CampoCambioSerializer
from cambios.models import CambiosDominio, CampoCambio


logger = logging.getLogger(__name__)


@cache_control(max_age=60*60*2, name='dispatch')
@method_decorator(cache_page(60*60*2), name='dispatch')  # 2 hours
class CambiosDominioViewSet(viewsets.ModelViewSet):
    queryset = CambiosDominio.objects.all()
    serializer_class = CambiosDominioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['-id']


@cache_control(max_age=60*60*2, name='dispatch')
@method_decorator(cache_page(60*60*2), name='dispatch')  # 2 hours
class CampoCambioViewSet(viewsets.ModelViewSet):
    queryset = CampoCambio.objects.all()
    serializer_class = CampoCambioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['campo', 'anterior', 'nuevo']
    ordering_fields = '__all__'
    ordering = ['-id']
