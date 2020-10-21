import random
from rest_framework import viewsets
from dominios.models import Dominio
from .serializer import DominioSerializer
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class DominioViewSet(viewsets.ModelViewSet):
    queryset = Dominio.objects.all()
    serializer_class = DominioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'nombre', 'expire']
    search_fields = ['nombre']
    ordering_fields = '__all__'
    ordering = ['nombre']


class NextPriorityDomainViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = Dominio.objects.all().order_by('-priority_to_update')[:100]
        random_item = random.choice(queryset)
        rand_id = random_item.id
        return Dominio.objects.filter(pk=rand_id)
    
    serializer_class = DominioSerializer
    