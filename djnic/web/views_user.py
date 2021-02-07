from django.views.generic.list import ListView

from mensajes.models import MensajeDestinado
from core.views import AnalyticsViewMixin
from mensajes.data import get_messages


class MensajeView(AnalyticsViewMixin, ListView):

    model = MensajeDestinado
    context_object_name = 'mensajes'
    template_name = "web/bootstrap-base/user/mensajes.html"

    def get_queryset(self):
        return get_messages(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Mensajes'
        context['site_description'] = f'Mensajes privados'

        return context
