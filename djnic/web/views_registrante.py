from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from registrantes.models import Registrante, TagForRegistrante
from dominios.data import get_ultimos_registrados
from registrantes.data import get_primeros_reg_creados


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class RegistranteView(DetailView):

    model = Registrante
    context_object_name = "registrante"
    template_name = "web/bootstrap-base/registrante.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Registrante de dominio {self.object.name}'
        context['site_description'] = f'Datos del registrante {self.object.name}'
        
        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class RegistrantesAntiguosView(ListView):

    model = Registrante
    context_object_name = "registrante"
    template_name = "web/bootstrap-base/registrantes/antiguos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Registrantes de dominio más antiguos'
        context['site_description'] = 'Lista de registrantes de dominio más antiguos'
        
        context['registrantes'] = get_primeros_reg_creados(limit=500)
        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class RubrosView(ListView):

    model = TagForRegistrante
    context_object_name = "rubros"
    template_name = "web/bootstrap-base/registrantes/rubros.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Rubros o Tags para registrante de dominio'
        context['site_description'] = 'Lista de rubros o Tags para registrante de dominio'
        
        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class RubroView(DetailView):

    model = TagForRegistrante
    context_object_name = "rubro"
    template_name = "web/bootstrap-base/registrantes/rubro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Rubro o Tag {self.object.nombre}'
        context['site_description'] = f'Datos sobre regitrantes etiquetados como {self.object.nombre}'

        # TODO context['ultimos_caidos'] = get_ultimos_caidos(limit=100)
        context['ultimos_registrados'] = get_ultimos_registrados(limit=100, etiqueta=self.object)
        
        return context
