from rest_framework import viewsets
from zonas.models import Zona
from .serializer import ZonaSerializer
from rest_framework.permissions import DjangoModelPermissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer
    permission_classes = [DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre']
    ordering_fields = '__all__'
    ordering = ['nombre']
