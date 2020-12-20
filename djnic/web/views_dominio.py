from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.detail import DetailView

from dominios.models import Dominio, STATUS_DISPONIBLE


@method_decorator(cache_control(max_age=settings.GENERAL_CACHE_SECONDS), name='dispatch')
@method_decorator(cache_page(settings.GENERAL_CACHE_SECONDS), name='dispatch')
class DominioView(DetailView):

    model = Dominio
    context_object_name = "dominio"
    template_name = "web/bootstrap-base/dominio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Dominio {self.object.full_domain()}'
        context['site_description'] = f'Datos del Dominio {self.object.full_domain()}'
        context['estado'] = 'Disponible' if self.object.estado == STATUS_DISPONIBLE else 'No disponible'

        # ordenar los cambios
        context['cambios'] = self.object.cambios.order_by('-momento')

        return context