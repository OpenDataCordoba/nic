import string
from core.views import AnalyticsViewMixin
from web.listas.utils import generate_lista_table
from django.views.generic.base import TemplateView


class ProvinciasArgentinasListView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Provincias Argentinas'
        context['site_description'] = 'Lista de provincias argentinas'
        # Lista de provincias argentinas
        data = [
            'buenosaires',
            'catamarca',
            'chaco',
            'chubut',
            'cordoba',
            'corrientes',
            'entrerios',
            'formosa',
            'jujuy',
            'lapampa',
            'larioja',
            'mendoza',
            'misiones',
            'neuquen',
            'rionegro',
            'salta',
            'sanjuan',
            'sanluis',
            'santacruz',
            'santafe',
            'santiagodelestero',
            'tierradelfuego',
            'tucuman',
        ]
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar', 'gob.ar'])
        context['data'] = dom_data

        return context


class DominiosUnaCaracterView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Dominios de una letra'
        context['site_description'] = 'Lista de dominios de una sola letra'
        # Lista de dominios de una letra
        data = list(string.ascii_lowercase) + list(string.digits)
        dom_data = generate_lista_table(data, zonas_relevantes=['ar', 'com.ar'])
        context['data'] = dom_data

        return context


class DominiosDosCaracteresView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Dominios de dos letras en .ar'
        context['site_description'] = 'Lista de dominios de dos letras en .ar'
        # Lista de dominios de dos letras
        data = []
        for char1 in string.ascii_lowercase + string.digits:
            for char2 in string.ascii_lowercase + string.digits:
                data.append(f"{char1}{char2}")
        dom_data = generate_lista_table(data, zonas_relevantes=['ar'])
        context['data'] = dom_data

        return context


class CiudadesArgentinasView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/listas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Lista de Ciudades Argentinas'
        context['site_description'] = 'Lista de ciudades argentinas'
        # Lista de ciudades argentinas
        data = [
            'buenosaires',
            'cordoba',
            'rosario',
            'mendoza',
            'laplata',
            'sanmiguel',
            'mardelplata',
            'salta',
            'santafe',
            'sanjuan',
            'resistencia',
            'bahiablanca',
            'parana',
            'merlo',
            'quilmes',
            'sansalvador',
            'guaymallen',
            'posadas',
            'sanrafael',
            'laferrere',
            'lanus',
            'godoycruz',
            'banfield',
            'riocuarto',
        ]
        data = sorted(data)
        dom_data = generate_lista_table(data, zonas_relevantes=['com.ar', 'ar', 'gob.ar'])
        context['data'] = dom_data

        return context
