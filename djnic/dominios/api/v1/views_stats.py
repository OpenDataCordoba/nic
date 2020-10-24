from datetime import timedelta
import json
import logging
from django.db.models import Count, F
from django.db.models.functions import Trunc
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from dominios.models import Dominio

logger = logging.getLogger(__name__)


class GeneralStatsViews(View):
    def get(self, request):
        ret = {}
        dominios = Dominio.objects.all()
        ret['total_dominios'] = dominios.count()
        # por zona

        # por estado
        por_estado = dominios.values('estado').annotate(total=Count('estado'))
        ret['estado'] = list(por_estado)

        # por dia de actualizacion, ultimos dias
        starts = timezone.now() - timedelta(days=15)
        por_dias = dominios.filter(data_updated__gt=starts)\
            .annotate(dia_updated=Trunc('data_updated', 'day'))\
            .order_by('-dia_updated')\
            .values('dia_updated')\
            .annotate(total=Count('dia_updated'))
        ret['actualizados_ultimos_dias'] = list(por_dias)

        # por semana de actualizacion, ultimas semanas
        starts = timezone.now() - timedelta(weeks=15)
        por_dias = dominios.filter(data_updated__gt=starts)\
            .annotate(week_updated=Trunc('data_updated', 'week'))\
            .order_by('-week_updated')\
            .values('week_updated')\
            .annotate(total=Count('week_updated'))
        ret['actualizados_ultimas_semanas'] = list(por_dias)

        # por estado
        por_zona = dominios.values(nombre_zona=F('zona__nombre')).annotate(total=Count('zona'))
        ret['zona'] = list(por_zona)

        prioridades = dominios.order_by('-priority_to_update')
        ret['prioridades'] = []
        for c in [1, 100, 1000, 5000, 10000, 20000]:
            if c < prioridades.count():
                ret['prioridades'].append(
                    {   'order': c,
                        'dominio': prioridades[c].full_domain(), 
                        'priority_to_update': prioridades[c].priority_to_update, 
                        'expire': prioridades[c].expire, 
                        'data_readed': prioridades[c].data_readed, 
                        'data_updated': prioridades[c].data_updated
                    })

        # return JsonResponse({'ok': False, 'error': 'Missing WhoAre version'}, status=400)
        return JsonResponse({'ok': True, 'data': ret}, status=200)

