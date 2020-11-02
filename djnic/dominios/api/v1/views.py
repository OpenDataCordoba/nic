from datetime import timedelta
import json
import logging
import random
from whoare.whoare import WhoAre
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.http import JsonResponse
from django.db.models import F, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from dominios.models import Dominio, STATUS_DISPONIBLE, STATUS_NO_DISPONIBLE, PreDominio
from zonas.models import Zona
from cambios.models import CampoCambio
from .serializer import DominioSerializer, CambiosDominioSerializer, FlatDominioSerializer, FlatPreDominioSerializer

logger = logging.getLogger(__name__)

class DominioViewSet(viewsets.ModelViewSet):
    queryset = Dominio.objects.all()
    serializer_class = DominioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'nombre', 'expire', 'registrante__legal_uid']
    search_fields = ['nombre', 'registrante__legal_uid']
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
            return JsonResponse({'ok': False, 'error': 'Missing WhoAre version'}, status=400)
        
        if final_data['whoare_version'] < '0.1.29':
            return JsonResponse({'ok': False, 'error': 'Unexpected WhoAre version'}, status=400)
        
        # skipp not-real domains
        if final_data['domain'].get('is_free', True):
            return JsonResponse({'ok': False, 'error': 'Unexpected REGISTERED domain'}, status=400)

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

@method_decorator(never_cache, name='dispatch')
class NextPriorityDomainViewSet(viewsets.ModelViewSet):
    
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        # definir si mando uno de los posibles nuevos o de la base comun
        nuevos = PreDominio.objects.all()
        pick = random.randint(1, 100)
        if pick > 70 or nuevos.count() == 0:
            prioritarios = Dominio.objects.all().order_by('-priority_to_update')[:100]
            random_item = random.choice(prioritarios)
            
            # remove priority
            random_item.priority_to_update = 0
            random_item.next_update_priority = timezone.now() + timedelta(days=15)    
            random_item.save()
            self.serializer_class = FlatDominioSerializer
            return Dominio.objects.filter(pk=random_item.id)
        else:
            nuevos = nuevos.order_by('-priority')[:100]
            random_item = random.choice(nuevos)
            random_item.priority = 0
            random_item.save()
            self.serializer_class = FlatPreDominioSerializer
            return PreDominio.objects.filter(pk=random_item.id)


class UltimosCaidosViewSet(viewsets.ModelViewSet):
    """ ultimo dominios que pasaron a estar disponibles """

    def get_queryset(self):
        campo_caidos = CampoCambio.objects.filter(
            campo='estado',
            anterior=STATUS_NO_DISPONIBLE,
            nuevo=STATUS_DISPONIBLE)\
                .order_by('-cambio__momento')[:100]
        ids = [cc.cambio.dominio.id for cc in campo_caidos]
        queryset = Dominio.objects.filter(id__in=ids)
        return queryset

    serializer_class = CambiosDominioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'nombre', 'expire']
    search_fields = ['nombre']
    ordering_fields = '__all__'
    ordering = ['nombre']


class UltimosRenovadosViewSet(viewsets.ModelViewSet):
    """ ultimo dominios que se renovaron """

    def get_queryset(self):
        campos = CampoCambio.objects.filter(
            campo='dominio_expire',
            nuevo__gt=F('anterior'))\
                .order_by('-cambio__momento')[:100]
        ids = [cc.cambio.dominio.id for cc in campos]
        queryset = Dominio.objects.filter(id__in=ids)
        return queryset

    serializer_class = CambiosDominioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'nombre', 'expire']
    search_fields = ['nombre']
    ordering_fields = '__all__'
    ordering = ['nombre']


class UltimosTranspasadosViewSet(viewsets.ModelViewSet):
    """ ultimo dominios que pasaron a nuevos dueños """

    def get_queryset(self):
        campos = CampoCambio.objects.filter(
            campo='registrant_legal_uid',
            nuevo__isnull=False,
            anterior__isnull=False)\
            .exclude(
                Q(nuevo__exact='') | Q(anterior__exact=''))\
            .order_by('-cambio__momento')[:100]

        ids = [cc.cambio.dominio.id for cc in campos]
        queryset = Dominio.objects.filter(id__in=ids)
        return queryset

    serializer_class = CambiosDominioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'nombre', 'expire']
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'expire']
    ordering = ['nombre']


class UltimosCambioDNSViewSet(viewsets.ModelViewSet):
    """ ultimo dominios que pasaron a nuevos dueños """

    def get_queryset(self):
        campos = CampoCambio.objects.filter(
            campo='DNS1',
            nuevo__isnull=False,
            anterior__isnull=False)\
            .exclude(
                Q(nuevo__exact='') | Q(anterior__exact=''))\
            .order_by('-cambio__momento')[:100]

        ids = [cc.cambio.dominio.id for cc in campos]
        queryset = Dominio.objects.filter(id__in=ids)
        return queryset

    serializer_class = CambiosDominioSerializer
    permission_classes = [DjangoModelPermissions]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'nombre', 'expire']
    search_fields = ['nombre']
    ordering_fields = '__all__'
    ordering = ['nombre']