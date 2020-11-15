from django.views.generic.base import TemplateView


class HomeView(TemplateView):

    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hola'] = 'Hola mundo'
        return context