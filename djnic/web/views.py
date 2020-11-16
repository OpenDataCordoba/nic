from django.views.generic.base import TemplateView


class HomeView(TemplateView):

    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'NIC Data'
        context['site_description'] = 'Sitio con información de registros de dominios argentinos'
        context['box1'] = {
            'counter': 900,
            'title': 'Titulo 1',
            'data_list': ','.join([str(x) for x in [3,6,9,12,0,0,12]])
        }
        return context