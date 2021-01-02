from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import TemplateView


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class StatsReadVtoView(TemplateView):

    template_name = "web/bootstrap-base/plataforma/stats-read-vto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas de lecturas por vencimiento'
        context['site_description'] = 'Dias desde la ultima lectura de domimios según fecha de vencimieeto del mismo'

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class StatsReadGeneralView(TemplateView):

    template_name = "web/bootstrap-base/plataforma/stats-read-general.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas de lecturas general de la plataforma'
        context['site_description'] = 'Estadistica de dominios revisados en la plataforma'

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class StatsRegistradosPorFechaView(TemplateView):

    template_name = "web/bootstrap-base/plataforma/registrados-por-fecha.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas de registros de dominios'
        context['site_description'] = 'Dominios registrados por fecha'

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class StatsVencimientosPorFechaView(TemplateView):

    template_name = "web/bootstrap-base/plataforma/vencimientos-por-fecha.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas de vencimientos de dominios'
        context['site_description'] = 'Dominios que vencen en cada fecha'

        return context
