from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from dominios.models import Dominio, STATUS_DISPONIBLE
from cambios.data import get_ultimos_caidos
from dominios.data import (get_ultimos_registrados, get_judicializados,
                           get_primeros_registrados, get_futuros,
                           get_por_caer)


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class DominioView(DetailView):

    model = Dominio
    context_object_name = "dominio"
    template_name = "web/bootstrap-base/dominio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Dominio {self.object.full_domain()}'
        context['site_description'] = f'Datos del Dominio {self.object.full_domain()}'
        context['estado'] = 'Disponible' if self.object.estado == STATUS_DISPONIBLE else 'No disponible'

        # ordenar los cambios
        context['cambios'] = self.object.cambios.order_by('-momento')

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class UltimosCaidos(TemplateView):

    template_name = "web/bootstrap-base/dominios/ultimos-caidos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        context['ultimos_caidos'] = get_ultimos_caidos(limit=500)

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class UltimosRegistrados(TemplateView):

    template_name = "web/bootstrap-base/dominios/ultimos-registrados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        context['ultimos_registrados'] = get_ultimos_registrados(limit=500)

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class DominiosAntiguosView(TemplateView):

    template_name = "web/bootstrap-base/dominios/antiguos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        context['dominios'] = get_primeros_registrados(limit=500)

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class Judicializados(TemplateView):

    template_name = "web/bootstrap-base/dominios/judicializados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios judicializados'
        context['site_description'] = 'Lista de los dominios vencidos sin caer'

        context['dominios'] = get_judicializados(limit=500)

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class DominiosVencimientoLargoView(TemplateView):
    """ Dominios que vencen más en el futuro """

    template_name = "web/bootstrap-base/dominios/futuros.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios futuros'
        context['site_description'] = 'Dominios que vencen más en el futuro'

        context['dominios'] = get_futuros(limit=500)

        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class PorCaerView(TemplateView):

    template_name = "web/bootstrap-base/dominios/por-caer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios apunto de caer'
        context['site_description'] = 'Dominios vencidos y listos para liberarse'

        context['por_caer'] = get_por_caer(limit=500)

        return context
