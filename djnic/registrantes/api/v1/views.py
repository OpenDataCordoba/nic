from datetime import timedelta
import json
import logging
import random
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from .serializer import RegistrantSerializer
from registrantes.models import Registrante


logger = logging.getLogger(__name__)

class RegistrantViewSet(viewsets.ModelViewSet):
    queryset = Registrante.objects.all()
    serializer_class = RegistrantSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'legal_uid']
    ordering_fields = '__all__'
    ordering = ['name']
