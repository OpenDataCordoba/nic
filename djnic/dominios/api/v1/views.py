from datetime import timedelta
import random
from django.utils import timezone
from rest_framework import viewsets
from dominios.models import Dominio
from .serializer import DominioSerializer
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.http import JsonResponse
from rest_framework.decorators import action


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

    @action(methods=['post'])
    def update_from_whoare(self, request):
        data = request.data

        if data.get('whoare_version', None) is None:
            return JsonResponse({'ok': False, 'error': 'Missing WhoAre version'}, status_code=400)
        
        if data['whoare_version'] < '0.1.29':
            return JsonResponse({'ok': False, 'error': 'Unexpected WhoAre version'}, status_code=400)
        
        "domain": {
            "base_name": 'fernet',
            "zone": 'com.ar',
            "is_free": False,
            "registered": wa.domain.registered,
            "changed": wa.domain.changed,
            "expire": wa.domain.expire
            },
        "registrant": {
            "name": wa.registrant.name,
            "legal_uid": wa.registrant.legal_uid,
            "created": wa.registrant.created,
            "changed": wa.registrant.changed
        },
        "dnss": ['ns2.sedoparking.com', 'ns1.sedoparking.com']



class NextPriorityDomainViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = Dominio.objects.all().order_by('-priority_to_update')[:100]
        random_item = random.choice(queryset)
        
        # remove priority until tomorrow
        random_item.priority_to_update = 0
        random_item.next_update_priority = timezone.now() + timedelta(days=3)    
        random_item.save()

        return Dominio.objects.filter(pk=random_item.id)
    
    serializer_class = DominioSerializer
    