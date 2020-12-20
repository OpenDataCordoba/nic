from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.detail import DetailView

from registrantes.models import Registrante


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