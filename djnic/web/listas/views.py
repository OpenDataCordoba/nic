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
        dom_data = generate_lista_table(data)
        context['data'] = dom_data

        return context
