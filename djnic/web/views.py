from datetime import timedelta
from django.conf import settings
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import TemplateView

from cambios.models import CampoCambio
from dominios.models import Dominio, STATUS_NO_DISPONIBLE, STATUS_DISPONIBLE
from zonas.models import GrupoZona
from dnss.models import Empresa
from registrantes.models import Registrante, TagForRegistrante, RegistranteTag


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

        # ultimos dominios caidos
        starts = timezone.now() - timedelta(days=2)
        ultimos_cambios = CampoCambio.objects\
            .filter(cambio__momento__gt=starts)\
            .filter(campo='estado', anterior=STATUS_NO_DISPONIBLE, nuevo=STATUS_DISPONIBLE)\
            .order_by('-cambio__momento')[:10]
        context['ultimos_caidos'] = ultimos_cambios
        
        # Ultimos dominios registrados
        context['ultimos_registrados'] = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE).order_by('-registered')[:10]

        # Empresas de hosting más usadas        
        hostings = Empresa.objects.all()
        hostings_all = hostings.annotate(total_dominios=Count('regexs__nameservers__dominios', filter=Q(regexs__nameservers__dominios__orden=1))).order_by('-total_dominios')[:10]
        context['hostings'] = hostings_all
        
        starts = timezone.now() - timedelta(days=30)
        hostings_last_30_days = hostings.filter(regexs__nameservers__dominios__dominio__registered__gt=starts)\
            .annotate(
                total_dominios=Count(
                    'regexs__nameservers__dominios', 
                    filter=Q(regexs__nameservers__dominios__orden=1)
                    )
                )\
            .order_by('-total_dominios')[:10]
        context['hostings_last_30_days'] = hostings_last_30_days
        

        # Nuevos dominios de registrantes tagueados
        starts = timezone.now() - timedelta(days=120)
        nuevos = Dominio.objects\
                    .filter(registered__gt=starts)\
                    .annotate(tags=Count('registrante__tags'))\
                    .filter(tags__gt=0)\
                    .order_by('-registered')

        context['news_from_tags'] = nuevos

        # Transferencias de dominios
        
        starts = timezone.now() - timedelta(days=120)
        transferencias = CampoCambio.objects\
            .filter(cambio__momento__gt=starts)\
            .filter(campo='registrant_legal_uid')\
            .exclude(Q(anterior__exact="") | Q(nuevo__exact=""))\
            .order_by('-cambio__momento')
        context['transferencias'] = transferencias[:10]

        # Transferencias de dominios tagueados
        tg_regs = Registrante.objects.annotate(total_tags=Count('tags'))\
                    .filter(total_tags__gt=0)
        tg_ids = [reg.legal_uid for reg in tg_regs]     
        
        transferencias_tag = transferencias.filter(
            Q(anterior__in=tg_ids) | Q(nuevo__in=tg_ids)
        )
        context['transferencias_tag'] = transferencias_tag[:10]

        # Dominios vencidos de registrantes tagueados
        timezone.now()
        nuevos = Dominio.objects\
                    .filter(expire__lt=timezone.now())\
                    .annotate(tags=Count('registrante__tags'))\
                    .filter(tags__gt=0)\
                    .order_by('expire')

        context['expired_from_tags'] = nuevos

        

        return context