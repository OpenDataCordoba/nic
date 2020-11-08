from datetime import timedelta
import json
import logging
from django.db.models import Count, F, Value, fields, ExpressionWrapper
from django.db.models.functions import Trunc
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from dominios.models import Dominio
from django.contrib.auth.mixins import PermissionRequiredMixin
logger = logging.getLogger(__name__)


class GeneralStatsView(PermissionRequiredMixin, View):
    
    permission_required = ['dominios.dominio.can_view']

    def get(self, request):
        ret = {}
        dominios = Dominio.objects.all()
        ret['total_dominios'] = dominios.count()
        
        # por estado
        por_estado = dominios.values('estado').annotate(total=Count('estado'))
        ret['estado'] = list(por_estado)

        # por dia de actualizacion, ultimos dias
        starts = timezone.now() - timedelta(days=1)
        por_horas = dominios.filter(data_updated__gt=starts)\
            .annotate(hora_updated=Trunc('data_updated', 'hour'))\
            .order_by('-hora_updated')\
            .values('hora_updated')\
            .annotate(total=Count('hora_updated'))
        ret['actualizados_ultimas_horas'] = list(por_horas)

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

        # return JsonResponse({'ok': False, 'error': 'Missing WhoAre version'}, status=400)
        return JsonResponse({'ok': True, 'data': ret}, status=200)


class PriorityView(PermissionRequiredMixin, View):

    permission_required = ['dominios.can_view']

    def get(self, request):
        ret = {}
        dominios = Dominio.objects.all()
        ret['total_dominios'] = dominios.count()
        
        prioridades = dominios.order_by('-priority_to_update')
        ret['prioridades'] = []
        for c in [1, 5, 10, 50, 100, 1000, 5000, 10000, 20000]:
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


class ReadingStatsView(PermissionRequiredMixin, View):
    
    permission_required = ['dominios.dominio.can_view']
    
    def get(self, request, **kwargs):
        ret = {}
        desde_dias = kwargs.get('desde_dias', 90)
        hasta_dias = kwargs.get('hasta_dias', 45)
        # por semana de actualizacion, ultimas semanas
        starts = timezone.now() - timedelta(days=desde_dias)
        ends = timezone.now() + timedelta(days=hasta_dias)
        ret['start'] = starts
        ret['end'] = ends
        dominios = Dominio.objects.exclude(data_readed__isnull=True).filter(expire__gt=starts, expire__lt=ends)
        data = {}
        total = 0
        for dominio in dominios:
            expire = dominio.expire.strftime("%Y-%m-%d")
            readed = dominio.data_readed
            if readed is None:  # (?)
                continue
            readed_since = int((timezone.now() - readed).total_seconds() // 86400)

            if expire not in data:
                data[expire] = {}
            if str(readed_since) not in data[expire]:
                data[expire][str(readed_since)] = 0
            data[expire][str(readed_since)] += 1
            total += 1

        ret['total'] = total
        ret['dates'] = data
            

        # TODO HELP ====================================
        # # now = Value(timezone.now(), output_field=fields.DateTimeField())
        # now = timezone.now()
        # # now = 'NOW()'
        # # now = 'epoch'
        # calc_read_since_days = ExpressionWrapper(
        #     now - F('data_readed'), 
        #     output_field=fields.DurationField()
        #     )
        # data = dominios.filter(expire__gt=starts, expire__lt=ends, data_readed__isnull=False)\
        #     .annotate(readed_day=Trunc('data_readed', 'day'))\
        #     .annotate(expire_day=Trunc('expire', 'day'))\
        #     .values('expire_day', 'readed_day')\
        #     .annotate(total=Count('expire_day'))\
        #     .order_by('-total')

        # # for res in data:
        # #     res['readed_since'] = res['readed_since'].total_seconds() / 86400
        # ret['expires'] = list(data)

        
        return JsonResponse({'ok': True, 'data': ret}, status=200)