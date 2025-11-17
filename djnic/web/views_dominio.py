from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from core.views import AnalyticsViewMixin
from dominios.models import Dominio, STATUS_DISPONIBLE
from cambios.data import get_ultimos_caidos
from dominios.data import (get_ultimos_registrados, get_judicializados,
                           get_primeros_registrados, get_futuros,
                           get_por_caer)


class DominioView(AnalyticsViewMixin, DetailView):

    model = Dominio
    context_object_name = "dominio"
    template_name = "web/bootstrap-base/dominio.html"

    def get_object(self):
        return Dominio.objects.get(uid=self.kwargs['uid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Dominio {self.object.full_domain()}'
        context['site_description'] = f'Datos del Dominio {self.object.full_domain()}'
        context['estado'] = 'Disponible' if self.object.estado == STATUS_DISPONIBLE else 'No disponible'

        # ordenar los cambios
        cambios = self.object.cambios.prefetch_related('campos').order_by('-momento')

        # Por más que NIC lo haya publicado no es de nuestro interes publicar
        # algunos datos persomnales
        campos_a_ocultar = [
            "admin_cp", "admin_domicilio", "admin_fax", "admin_tel", "reg_cp",
            "reg_documento", "reg_domicilio", "reg_domicilio_exterior", "reg_fax",
            "reg_fax_exterior", "reg_telefono", "reg_telefono_exterior",
            "registrant_legal_uid", "resp_cp", "resp_domicilio", "resp_fax",
            "resp_telefono", "tech_cp", "tech_domicilio", "tech_fax", "tech_telefono"
        ]

        ncambios = []
        for cambio in cambios:
            chg = {
                'have_changes': cambio.have_changes,
                'momento': cambio.momento,
                'campos_cambiados': []
            }
            if cambio.have_changes:
                for campo in cambio.campos.all():
                    campo_dict = {
                        'campo': campo.campo,
                        'anterior': campo.anterior,
                        'nuevo': campo.nuevo
                    }
                    if campo.campo in campos_a_ocultar:
                        campo_dict['anterior'] = '[protegido]'
                        campo_dict['nuevo'] = '[protegido]'

                    chg['campos_cambiados'].append(campo_dict)

            ncambios.append(chg)

        context['cambios'] = ncambios

        return context


class UltimosCaidos(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/ultimos-caidos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        context['ultimos_caidos'] = get_ultimos_caidos(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['ultimos_caidos'] = context['ultimos_caidos'][:5]

        return context


class UltimosRegistrados(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/ultimos-registrados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios registrados'
        context['site_description'] = 'Lista de los últimos dominios registrados'

        context['ultimos_registrados'] = get_ultimos_registrados(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['ultimos_registrados'] = context['ultimos_registrados'][:5]

        return context


class DominiosAntiguosView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/antiguos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        context['dominios'] = get_primeros_registrados(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['dominios'] = context['dominios'][:5]

        return context


class Judicializados(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/judicializados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios judicializados'
        context['site_description'] = 'Lista de los dominios vencidos sin caer'

        context['dominios'] = get_judicializados(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['dominios'] = context['dominios'][:5]

        return context


class DominiosVencimientoLargoView(AnalyticsViewMixin, TemplateView):
    """ Dominios que vencen más en el futuro """

    template_name = "web/bootstrap-base/dominios/futuros.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios futuros'
        context['site_description'] = 'Dominios que vencen más en el futuro'

        context['dominios'] = get_futuros(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['dominios'] = context['dominios'][:5]

        return context


class PorCaerView(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/por-caer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Dominios apunto de caer'
        context['site_description'] = 'Dominios vencidos y listos para liberarse'

        context['por_caer'] = get_por_caer(limit=500)

        # limit for non logged users
        if not self.request.user.is_authenticated:
            context['por_caer'] = context['por_caer'][:5]

        return context
