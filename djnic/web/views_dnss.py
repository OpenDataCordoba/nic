from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from dnss.models import Empresa
from dnss.data import get_hosting_usados, get_dominios_from_hosting


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class HostingView(DetailView):

    model = Empresa
    context_object_name = "hosting"
    template_name = "web/bootstrap-base/hosting/hosting.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Hosting {self.object.nombre}'
        context['site_description'] = f'Datos del proveedor de hosting {self.object.nombre}'

        context['dominios'] = get_dominios_from_hosting(hosting=self.object, limit=5)
        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class HostingsView(ListView):

    model = Empresa
    context_object_name = "hostings"
    template_name = "web/bootstrap-base/hosting/hostings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Hostings mas usados'
        context['site_description'] = 'Proveedores de hostings mas usados según DNS1'

        context['hostings'] = get_hosting_usados(limit=100)
        context['value_is'] = 'Dominios'
        return context


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class Hostings30View(ListView):

    model = Empresa
    context_object_name = "hostings"
    template_name = "web/bootstrap-base/hosting/hostings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Hostings mas usados (30 días)'
        context['site_description'] = 'Proveedores de hostings mas usados según DNS1 para dominios creados en los últimos 30 días'

        context['hostings'] = get_hosting_usados(limit=100, days_ago=30)
        context['value_is'] = 'Dominios (ult 30 días)'
        return context
