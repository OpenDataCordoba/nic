from datetime import timedelta
import json
import logging
from django.conf import settings
from django.db.models import Count, F, Value, fields, ExpressionWrapper
from django.db.models.functions import Trunc
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from dominios.models import Dominio
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.cache import cache_page, never_cache, cache_control

logger = logging.getLogger(__name__)

@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class GeneralStatsView(PermissionRequiredMixin, View):

    permission_required = []

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
            .order_by('hora_updated')\
            .values('hora_updated')\
            .annotate(total=Count('hora_updated'))
        ret['actualizados_ultimas_horas'] = list(por_horas)

        # por dia de actualizacion, ultimos dias
        starts = timezone.now() - timedelta(days=15)
        por_dias = dominios.filter(data_updated__gt=starts)\
            .annotate(dia_updated=Trunc('data_updated', 'day'))\
            .order_by('dia_updated')\
            .values('dia_updated')\
            .annotate(total=Count('dia_updated'))
        ret['actualizados_ultimos_dias'] = list(por_dias)

        # por semana de actualizacion, ultimas semanas
        starts = timezone.now() - timedelta(weeks=15)
        por_semanas = dominios.filter(data_updated__gt=starts)\
            .annotate(week_updated=Trunc('data_updated', 'week'))\
            .order_by('week_updated')\
            .values('week_updated')\
            .annotate(total=Count('week_updated'))
        ret['actualizados_ultimas_semanas'] = list(por_semanas)

        # por estado
        por_zona = dominios.values(nombre_zona=F('zona__nombre')).annotate(total=Count('zona'))
        ret['zona'] = list(por_zona)

        headers = ['hora', 'dominios actualizados']
        google_chart_data = [headers]
        for hora in por_horas:
            line = [hora['hora_updaed'], hora['total']]
            google_chart_data.append(line)

        ret['google_chart_data'] = {'hora': google_chart_data}

        headers = ['dia', 'dominios actualizados']
        google_chart_data = [headers]
        for dia in por_dias:
            line = [dia['dia_updaed'], dia['total']]
            google_chart_data.append(line)

        ret['google_chart_data']['dia'] = google_chart_data

        headers = ['semana', 'dominios actualizados']
        google_chart_data = [headers]
        for semana in por_semanas:
            line = [semana['week_updated'], semana['total']]
            google_chart_data.append(line)

        ret['google_chart_data']['semana'] = google_chart_data

        # return JsonResponse({'ok': False, 'error': 'Missing WhoAre version'}, status=400)
        return JsonResponse({'ok': True, 'data': ret}, status=200)


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
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


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class ReadingStatsView(PermissionRequiredMixin, View):

    permission_required = []

    def get(self, request, **kwargs):
        ret = {}
        desde_dias = int(kwargs.get('desde_dias', '90'))
        hasta_dias = int(kwargs.get('hasta_dias', '45'))
        # por semana de actualizacion, ultimas semanas
        starts = timezone.now() - timedelta(days=desde_dias)
        ends = timezone.now() + timedelta(days=hasta_dias)
        ret['start'] = starts
        ret['end'] = ends
        dominios = Dominio.objects.exclude(data_readed__isnull=True).filter(expire__gt=starts, expire__lt=ends).order_by('expire')
        data = {}
        total = 0
        columns = ['+300', '150-300', '60-150', '30-60', '10-30', '5-10', '4', '3', '2', '1', '0']

        for dominio in dominios:
            expire = dominio.expire.strftime("%Y-%m-%d")

            readed = dominio.data_readed
            if readed is None:  # (?)
                continue
            readed_since = (timezone.now() - readed).days

            if expire not in data:
                data[expire] = {k: 0 for k in columns}
            if readed_since >= 300:
                rs = '+300'
            elif readed_since >= 150:
                rs = '150-300'
            elif readed_since >= 60:
                rs = '60-150'
            elif readed_since >= 30:
                rs = '30-60'
            elif readed_since >= 10:
                rs = '10-30'
            elif readed_since >= 5:
                rs = '5-10'
            else:
                rs = str(readed_since)

            data[expire][rs] += 1
            total += 1

        ret['total'] = total
        ret['dates'] = data

        # return google chart comaptible data
        headers = ['date'] + columns
        google_chart_data = [headers]
        for expire_day in data:
            line = [expire_day] + [data[expire_day][k] for k in data[expire_day]]
            google_chart_data.append(line)

        ret['google_chart_data'] = google_chart_data

        return JsonResponse({'ok': True, 'data': ret}, status=200)