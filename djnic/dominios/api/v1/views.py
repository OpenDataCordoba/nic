from datetime import timedelta
import json
import logging
import random
from whoare.whoare import WhoAre
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.http import JsonResponse
from rest_framework.decorators import action
from dominios.models import Dominio
from zonas.models import Zona
from .serializer import DominioSerializer

logger = logging.getLogger(__name__)

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

    @action(methods=['post'], detail=False)
    def update_from_whoare(self, request):
        data = request.data  # require to be parsed
        logger.info(f'update_from_whoare: {data}')
        
        real_data_str = data['domain']
        logger.info(f'real data: {real_data_str}')
        
        # final_data = ast.literal_eval(real_data_str)
        final_data = json.loads(real_data_str)
        
        if final_data.get('whoare_version', None) is None:
            return JsonResponse({'ok': False, 'error': 'Missing WhoAre version'}, status_code=400)
        
        if final_data['whoare_version'] < '0.1.29':
            return JsonResponse({'ok': False, 'error': 'Unexpected WhoAre version'}, status_code=400)
        
        wa = WhoAre()
        wa.from_dict(final_data)
        
        zona, _ = Zona.objects.get_or_create(nombre=wa.domain.zone)
        dominio, dominio_created = Dominio.objects.get_or_create(
            nombre=wa.domain.base_name,
            zona=zona
            )
        
        cambios = dominio.update_from_wa_object(wa, just_created=dominio_created)
        res = {
            'ok': True,
            'created': dominio_created,
            'cambios': cambios
        }
        return JsonResponse(res)


class NextPriorityDomainViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = Dominio.objects.all().order_by('-priority_to_update')[:100]
        random_item = random.choice(queryset)
        
        # remove priority
        random_item.priority_to_update = 0
        random_item.next_update_priority = timezone.now() + timedelta(days=3)    
        random_item.save()

        return Dominio.objects.filter(pk=random_item.id)
    
    serializer_class = DominioSerializer
    