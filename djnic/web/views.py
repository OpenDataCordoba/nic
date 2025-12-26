import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.views.generic.base import TemplateView
from django.views.generic import FormView

from web.forms import SearchForm
from cambios.data import get_ultimos_caidos, get_ultimas_transferencias
from dominios.data import get_ultimos_registrados
from dnss.data import get_hosting_usados
from core.data import get_search_results
from core.views import AnalyticsViewMixin
from zonas.models import Zona


class HomeView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'NIC Data'
        context['site_description'] = 'Sitio con información de registros de dominios argentinos'

        zona_id = self.request.GET.get('zona')
        zona = None
        if zona_id:
            try:
                zona = Zona.objects.get(id=zona_id)
            except Zona.DoesNotExist:
                zona = None
        context['zona_seleccionada'] = zona
        context['zonas'] = Zona.objects.all()

        context['ultimos_caidos'] = get_ultimos_caidos(limit=5, zona=zona)
        context['ultimos_registrados'] = get_ultimos_registrados(limit=5, zona=zona)
        # context['hostings'] = get_hosting_usados(days_ago=0, limit=5, zona=zona)
        # context['hostings_last_30_days'] = get_hosting_usados(days_ago=30, limit=5, zona=zona)
        context['news_from_tags'] = get_ultimos_registrados(limit=5, de_registrantes_etiquetados=True, zona=zona)
        context['transferencias'] = get_ultimas_transferencias(limit=5, zona=zona)
        return context


class TermsView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/terms_of_service.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Términos y condiciones'
        context['site_description'] = 'Términos y condiciones de la app DominiosAR'

        return context


class PrivaciPolicyView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Política de privacidad'
        context['site_description'] = 'Política de privacidad de la app DominiosAR'

        return context


class AboutView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Acerca de Dominios Argentinos'
        context['site_description'] = 'Dominios Argentinos es un proyecto de OpenDataCordoba'

        return context


class SearchResultsView(AnalyticsViewMixin, FormView):

    form_class = SearchForm
    template_name = "web/bootstrap-base/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Acerca de Dominios Argentinos'
        context['site_description'] = 'Dominios Argentinos es un proyecto de OpenDataCordoba'

        query = self.request.GET.get('query')
        context['query'] = query

        context.update(get_search_results(query))

        return context


class LoginView(TemplateView):

    template_name = "web/bootstrap-base/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Login'
        context['site_description'] = 'Registrarse o acceder a DominiosAR'

        return context


def robots_txt(request):
    """Serve robots.txt file"""

    robots_path = os.path.join(settings.BASE_DIR, 'web', 'static', 'robots.txt')

    try:
        return FileResponse(open(robots_path, 'rb'), content_type='text/plain')
    except FileNotFoundError:
        raise Http404("robots.txt not found")
