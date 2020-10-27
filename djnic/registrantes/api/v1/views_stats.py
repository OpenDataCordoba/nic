from datetime import timedelta
import json
import logging
from django.db.models import Count, F
from django.db.models.functions import Trunc
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from registrantes.models import Registrante
from django.contrib.auth.mixins import PermissionRequiredMixin
logger = logging.getLogger(__name__)


class GeneralStatsView(View, PermissionRequiredMixin):
    
    permission_required = ['registrantes.registrante.can_view']

    def get(self, request):
        ret = {}
        registrantes = Registrante.objects.all()
        ret['total_registrantes'] = registrantes.count()
        
        # por año de creacion
        por_anios = registrantes.annotate(year_created=Trunc('created', 'year'))\
            .order_by('-year_created')\
            .values('year_created')\
            .annotate(total=Count('year_created'))[:200]
        ret['creados_por_anio'] = list(por_anios)

        # return JsonResponse({'ok': False, 'error': 'Missing WhoAre version'}, status=400)
        return JsonResponse({'ok': True, 'data': ret}, status=200)


class MayoresRegistrantesView(View, PermissionRequiredMixin):

    permission_required = ['registrantes.registrante.can_view']

    def get(self, request):
        ret = {}
        registrantes = Registrante.objects.annotate(total_dominios=Count('dominios'))\
            .order_by('-total_dominios')\
            .values('id', 'name', 'legal_uid', 'total_dominios')

        ret['mayores_registrantes'] = list(registrantes)

        return JsonResponse({'ok': True, 'data': ret}, status=200)