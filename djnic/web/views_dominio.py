from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from core.views import AnalyticsViewMixin
from dominios.models import Dominio, STATUS_DISPONIBLE
from cambios.data import get_ultimos_caidos
from dominios.data import (get_ultimos_registrados, get_judicializados,
                           get_primeros_registrados, get_futuros,
                           get_por_caer)


class DominioView(AnalyticsViewMixin, DetailView):

    model = Dominio
    context_object_name = "dominio"
    template_name = "web/bootstrap-base/dominio.html"

    def get_object(self):
        return Dominio.objects.get(uid=self.kwargs['uid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Dominio {self.object.full_domain()}'
        context['site_description'] = f'Datos del Dominio {self.object.full_domain()}'
        context['estado'] = 'Disponible' if self.object.estado == STATUS_DISPONIBLE else 'No disponible'

        # ordenar los cambios
        context['cambios'] = self.object.cambios.order_by('-momento')

        return context


class UltimosCaidos(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/ultimos-caidos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        context['ultimos_caidos'] = get_ultimos_caidos(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['ultimos_caidos'] = context['ultimos_caidos'][:5]

        return context


class UltimosRegistrados(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/ultimos-registrados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        context['ultimos_registrados'] = get_ultimos_registrados(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['ultimos_registrados'] = context['ultimos_registrados'][:5]

        return context


class DominiosAntiguosView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/antiguos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        context['dominios'] = get_primeros_registrados(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['dominios'] = context['dominios'][:5]

        return context


class Judicializados(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/judicializados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios judicializados'
        context['site_description'] = 'Lista de los dominios vencidos sin caer'

        context['dominios'] = get_judicializados(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['dominios'] = context['dominios'][:5]

        return context


class DominiosVencimientoLargoView(AnalyticsViewMixin, TemplateView):
    """ Dominios que vencen más en el futuro """

    template_name = "web/bootstrap-base/dominios/futuros.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios futuros'
        context['site_description'] = 'Dominios que vencen más en el futuro'

        context['dominios'] = get_futuros(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['dominios'] = context['dominios'][:5]

        return context


class PorCaerView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/por-caer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios apunto de caer'
        context['site_description'] = 'Dominios vencidos y listos para liberarse'

        context['por_caer'] = get_por_caer(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['por_caer'] = context['por_caer'][:5]

        return context
