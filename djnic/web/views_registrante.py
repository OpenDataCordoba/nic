from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from core.views import AnalyticsViewMixin
from registrantes.models import Registrante, TagForRegistrante
from dominios.data import get_ultimos_registrados
from registrantes.data import get_primeros_reg_creados, get_mayores_registrantes


class RegistranteView(AnalyticsViewMixin, DetailView):

    model = Registrante
    context_object_name = "registrante"
    template_name = "web/bootstrap-base/registrante.html"

    def get_object(self):
        return Registrante.objects.get(uid=self.kwargs['uid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Registrante de dominio {self.object.name}'
        context['site_description'] = f'Datos del registrante {self.object.name}'

        return context


class RegistrantesAntiguosView(AnalyticsViewMixin, ListView):

    model = Registrante
    context_object_name = "registrante"
    template_name = "web/bootstrap-base/registrantes/antiguos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Registrantes de dominio más antiguos'
        context['site_description'] = 'Lista de registrantes de dominio más antiguos'

        context['registrantes'] = get_primeros_reg_creados(limit=500)
        return context


class MayoresRegistrantesView(AnalyticsViewMixin, ListView):

    model = Registrante
    context_object_name = "registrante"
    template_name = "web/bootstrap-base/registrantes/mayores.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Mayores registrantes'
        context['site_description'] = 'Lista de registrantes con más dominio registrados'

        context['registrantes'] = get_mayores_registrantes(limit=50)
        return context


class RubrosView(AnalyticsViewMixin, ListView):

    model = TagForRegistrante
    context_object_name = "rubros"
    template_name = "web/bootstrap-base/registrantes/rubros.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Rubros o Tags para registrante de dominio'
        context['site_description'] = 'Lista de rubros o Tags para registrante de dominio'

        return context


class RubroView(AnalyticsViewMixin, DetailView):

    model = TagForRegistrante
    context_object_name = "rubro"
    template_name = "web/bootstrap-base/registrantes/rubro.html"

    def get_object(self):
        return TagForRegistrante.objects.get(uid=self.kwargs['uid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Rubro o Tag {self.object.nombre}'
        context['site_description'] = f'Datos sobre regitrantes etiquetados como {self.object.nombre}'

        # TODO context['ultimos_caidos'] = get_ultimos_caidos(limit=100)
        context['ultimos_registrados'] = get_ultimos_registrados(limit=100, etiqueta=self.object)
        context['mayores_registrantes'] = get_mayores_registrantes(limit=50, etiqueta=self.object)

        webpush = {"group": f'rubro-{self.kwargs["uid"]}'}
        context['webpush'] = webpush
        return context
