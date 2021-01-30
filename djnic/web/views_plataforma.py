from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import TemplateView

from core.views import AnalyticsViewMixin


class StatsReadVtoView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/plataforma/stats-read-vto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas de lecturas por vencimiento'
        context['site_description'] = 'Dias desde la ultima lectura de domimios según fecha de vencimieeto del mismo'

        return context


class StatsReadGeneralView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/plataforma/stats-read-general.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas de lecturas general de la plataforma'
        context['site_description'] = 'Estadistica de dominios revisados en la plataforma'

        return context


class StatsRegistradosPorFechaView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/plataforma/registrados-por-fecha.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas de registros de dominios'
        context['site_description'] = 'Dominios registrados por fecha'

        return context


class StatsVencimientosPorFechaView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/plataforma/vencimientos-por-fecha.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas de vencimientos de dominios'
        context['site_description'] = 'Dominios que vencen en cada fecha'

        return context
