from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from core.views import AnalyticsViewMixin
from cambios.models import CampoCambio
from dnss.models import Empresa, DNS
from cambios.data import get_perdidas_dns
from dnss.data import get_hosting_usados, get_dominios_from_hosting, get_orphan_dns
from dominios.data import dominios_sin_dns


class HostingView(AnalyticsViewMixin, DetailView):

    model = Empresa
    context_object_name = "hosting"
    template_name = "web/bootstrap-base/hosting/hosting.html"

    def get_object(self):
        return Empresa.objects.get(uid=self.kwargs['uid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Hosting {self.object.nombre}'
        context['site_description'] = f'Datos del proveedor de hosting {self.object.nombre}'

        dominios = get_dominios_from_hosting(hosting=self.object, limit=0)
        context['total_dominios'] = dominios.count()
        context['ultimos_dominios'] = dominios[:5]
        return context


class HostingsView(AnalyticsViewMixin, ListView):

    model = Empresa
    context_object_name = "hostings"
    template_name = "web/bootstrap-base/hosting/hostings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Hostings mas usados'
        context['site_description'] = 'Proveedores de hostings mas usados según DNS1'

        context['hostings'] = get_hosting_usados(limit=250)
        context['dominios_sin_dns'] = dominios_sin_dns(limit=0).count()
        context['huerfanos'] = get_orphan_dns(limit=250)
        context['value_is'] = 'Dominios'
        return context


class Hostings30View(AnalyticsViewMixin, ListView):

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


class DNSView(AnalyticsViewMixin, DetailView):

    model = DNS
    context_object_name = "dns"
    template_name = "web/bootstrap-base/hosting/dns.html"

    def get_object(self):
        return DNS.objects.get(uid=self.kwargs['uid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'DNS {self.object.dominio}'
        context['site_description'] = f'Datos del DNS {self.object.dominio}'

        context['dominios'] = self.object.dominios.order_by('dominio__nombre')
        return context


class PerdidasView(AnalyticsViewMixin, ListView):

    model = CampoCambio
    context_object_name = "campo"
    template_name = "web/bootstrap-base/hosting/perdidas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Perdidas de clientes'
        context['site_description'] = 'Perdidas de clientes por empresas de hosting'

        # ordenar los cambios
        context['perdidas'] = get_perdidas_dns(days_ago=30)

        return context
