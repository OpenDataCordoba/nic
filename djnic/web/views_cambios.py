from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from cambios.models import CampoCambio
from cambios.data import get_renovaciones


class RenovacionesView(ListView):

    model = CampoCambio
    context_object_name = "campo"
    template_name = "web/bootstrap-base/dominios/renovaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Renovaciones de dominio'
        context['site_description'] = 'Lista de últimos dominios renovados'

        # ordenar los cambios
        context['campos'] = get_renovaciones(limit=200)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['campos'] = context['campos'][:5]

        return context


class RenovacionesRarasView(ListView):

    model = CampoCambio
    context_object_name = "campo"
    template_name = "web/bootstrap-base/dominios/renovaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Renovaciones de dominio'
        context['site_description'] = 'Lista de últimos dominios renovados con cambios diferente a 365 días'

        # ordenar los cambios
        context['campos'] = get_renovaciones(limit=200, solo_fallados=True)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['campos'] = context['campos'][:5]

        return context


class RenovacionesHaciaAtrasView(ListView):

    model = CampoCambio
    context_object_name = "campo"
    template_name = "web/bootstrap-base/dominios/renovaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Renovaciones de dominio hacia atras'
        context['site_description'] = 'Lista de últimos dominios renovados con fecha de vencimiento que cambia hacia el pasado'

        # ordenar los cambios
        context['campos'] = get_renovaciones(limit=200, solo_hacia_atras=True)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['campos'] = context['campos'][:5]

        return context
