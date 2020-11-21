from datetime import timedelta
from django.conf import settings
from django.db.models import Count
from django.db.models.functions import Trunc
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import TemplateView

from cambios.models import CampoCambio
from dominios.models import Dominio, STATUS_NO_DISPONIBLE, STATUS_DISPONIBLE
from zonas.models import GrupoZona

@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class HomeView(TemplateView):

    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'NIC Data'
        context['site_description'] = 'Sitio con información de registros de dominios argentinos'

        starts = timezone.now() - timedelta(days=15)
        context['boxes'] = []
        grupos = GrupoZona.objects.filter(published=True)
        for grupo in grupos:
            
            dominios_grupo = Dominio.objects.filter(zona__grupos__grupo=grupo, estado=STATUS_NO_DISPONIBLE)
            ultimos_dias_grupo = dominios_grupo.filter(data_updated__gt=starts)

            grouped = ultimos_dias_grupo.annotate(dia_updated=Trunc('data_updated', 'day'))\
                .order_by('-dia_updated')\
                .values('dia_updated')\
                .annotate(total=Count('dia_updated'))
            
            box =  {
                    'counter': dominios_grupo.count(),
                    'title': grupo.nombre,
                    'data_list': ','.join([str(x['total']) for x in grouped]),
                    'type': 'country'}

            context['boxes'].append(box)
            
            
            zonas = grupo.zonas.filter(published=True)
            for zonag in zonas:
                zona = zonag.zona
                dominios = dominios_grupo.filter(zona=zona)
                ultimos_dias = ultimos_dias_grupo.filter(zona=zona)\
                    .annotate(dia_updated=Trunc('data_updated', 'day'))\
                    .order_by('-dia_updated')\
                    .values('dia_updated')\
                    .annotate(total=Count('dia_updated'))
                
                box =  {
                    'counter': dominios.count(),
                    'title': zona.nombre,
                    'data_list': ','.join([str(x['total']) for x in ultimos_dias]),
                    'type': 'zone'}

                context['boxes'].append(box)

        starts = timezone.now() - timedelta(days=2)
        ultimos_cambios = CampoCambio.objects\
            .filter(cambio__momento__gt=starts)\
            .filter(campo='estado', anterior=STATUS_NO_DISPONIBLE, nuevo=STATUS_DISPONIBLE)\
            .order_by('-cambio__momento')[:50]
        context['ultimos_caidos'] = ultimos_cambios
        return context