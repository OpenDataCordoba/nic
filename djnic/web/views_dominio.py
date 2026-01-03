from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden

from core.views import AnalyticsViewMixin
from dominios.models import Dominio, STATUS_DISPONIBLE
from cambios.data import get_ultimos_caidos
from dominios.data import (get_ultimos_registrados, get_judicializados,
                           get_primeros_registrados, get_futuros,
                           get_por_caer)
from zonas.models import Zona
from subscriptions.models import SubscriptionTarget, UserSubscription, EVENT_TYPE_CHOICES


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

        # Subscription info for staff users
        context['is_staff'] = self.request.user.is_staff if self.request.user.is_authenticated else False
        context['user_subscription'] = None
        context['event_type_choices'] = EVENT_TYPE_CHOICES
        context['delivery_mode_choices'] = UserSubscription.DELIVERY_MODE_CHOICES

        if context['is_staff']:
            # Check if user has an existing subscription to this domain
            ct = ContentType.objects.get_for_model(Dominio)
            target = SubscriptionTarget.objects.filter(
                content_type=ct,
                object_id=self.object.id
            ).first()

            if target:
                context['user_subscription'] = UserSubscription.objects.filter(
                    user=self.request.user,
                    target=target
                ).first()

        return context


class UltimosCaidos(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/ultimos-caidos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios caidos'
        context['site_description'] = 'Lista de los últimos dominios caidos'

        zona_id = self.request.GET.get('zona')
        zona = None
        if zona_id:
            try:
                zona = Zona.objects.get(id=zona_id)
            except Zona.DoesNotExist:
                zona = None
        context['zona_seleccionada'] = zona
        context['zonas'] = Zona.objects.all()

        # Authenticated users see 500, anonymous users see 5
        limit = 500 if self.request.user.is_authenticated else 5
        context['ultimos_caidos'] = get_ultimos_caidos(limit=limit, zona=zona)

        return context


class UltimosRegistrados(AnalyticsViewMixin, TemplateView):

    template_name = "web/bootstrap-base/dominios/ultimos-registrados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Ultimos dominios registrados'
        context['site_description'] = 'Lista de los últimos dominios registrados'

        zona_id = self.request.GET.get('zona')
        zona = None
        if zona_id:
            try:
                zona = Zona.objects.get(id=zona_id)
            except Zona.DoesNotExist:
                zona = None
        context['zona_seleccionada'] = zona
        context['zonas'] = Zona.objects.all()

        context['ultimos_registrados'] = get_ultimos_registrados(limit=500, zona=zona)

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


class SubscribeToDomainView(View):
    """Create or update a subscription to a domain - Staff only"""

    def post(self, request, uid):
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo usuarios staff pueden realizar esta acción")

        dominio = get_object_or_404(Dominio, uid=uid)

        # Get or create the subscription target for this domain
        ct = ContentType.objects.get_for_model(Dominio)
        target, _ = SubscriptionTarget.objects.get_or_create(
            content_type=ct,
            object_id=dominio.id
        )

        # Get form data
        event_types = request.POST.getlist('event_types')
        delivery_mode = request.POST.get('delivery_mode', 'immediate')

        if not event_types:
            messages.error(request, 'Debe seleccionar al menos un tipo de evento')
            return redirect('dominio', uid=uid)

        # Create or update subscription
        subscription, created = UserSubscription.objects.update_or_create(
            user=request.user,
            target=target,
            defaults={
                'event_types': event_types,
                'delivery_mode': delivery_mode,
                'is_active': True
            }
        )

        if created:
            messages.success(request, f'Ahora sigues el dominio {dominio.full_domain()}')
        else:
            messages.success(request, f'Suscripción actualizada para {dominio.full_domain()}')

        return redirect('dominio', uid=uid)


class UnsubscribeFromDomainView(View):
    """Remove a subscription from a domain - Staff only"""

    def post(self, request, uid):
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo usuarios staff pueden realizar esta acción")

        dominio = get_object_or_404(Dominio, uid=uid)

        ct = ContentType.objects.get_for_model(Dominio)
        target = SubscriptionTarget.objects.filter(
            content_type=ct,
            object_id=dominio.id
        ).first()

        if target:
            deleted, _ = UserSubscription.objects.filter(
                user=request.user,
                target=target
            ).delete()

            if deleted:
                messages.success(request, f'Dejaste de seguir {dominio.full_domain()}')
            else:
                messages.warning(request, 'No tenías una suscripción activa')
        else:
            messages.warning(request, 'No tenías una suscripción activa')

        return redirect('dominio', uid=uid)
