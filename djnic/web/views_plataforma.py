from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import TemplateView


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class StatsView(TemplateView):

    template_name = "web/bootstrap-base/plataforma/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Estadisticas'
        context['site_description'] = 'Estadísticas del proyecto de dominios argentinos'

        return context
