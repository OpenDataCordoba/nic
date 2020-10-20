from rest_framework import viewsets
from dominios.models import Dominio
from .serializer import DominioSerializer


class DominioViewSet(viewsets.ModelViewSet):
    queryset = Dominio.objects.all()
    serializer_class = DominioSerializer
