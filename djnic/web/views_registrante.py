from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden

from core.views import AnalyticsViewMixin
from registrantes.models import Registrante, TagForRegistrante, RegistranteTag
from dominios.data import get_ultimos_registrados
from registrantes.data import get_primeros_reg_creados, get_mayores_registrantes
from subscriptions.models import SubscriptionTarget, UserSubscription, EVENT_TYPE_CHOICES


class RegistranteView(AnalyticsViewMixin, DetailView):

    model = Registrante
    context_object_name = "registrante"
    template_name = "web/bootstrap-base/registrante.html"

    def get_object(self):
        return Registrante.objects.get(uid=self.kwargs['uid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Registrante de dominio {self.object.name}'
        context['site_description'] = f'Datos del registrante {self.object.name}'
        context['dominios'] = self.object.dominios.all().order_by('expire')

        # Tags para usuarios staff
        context['registrante_tags'] = self.object.tags.all()
        context['all_tags'] = TagForRegistrante.objects.all().order_by('nombre')
        context['is_staff'] = self.request.user.is_staff if self.request.user.is_authenticated else False

        # Subscription info for staff users
        context['user_subscription'] = None
        context['event_type_choices'] = EVENT_TYPE_CHOICES
        context['delivery_mode_choices'] = UserSubscription.DELIVERY_MODE_CHOICES

        if context['is_staff']:
            ct = ContentType.objects.get_for_model(Registrante)
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


class RegistrantesAntiguosView(AnalyticsViewMixin, ListView):

    model = Registrante
    context_object_name = "registrante"
    template_name = "web/bootstrap-base/registrantes/antiguos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Registrantes de dominio más antiguos'
        context['site_description'] = 'Lista de registrantes de dominio más antiguos'

        context['registrantes'] = get_primeros_reg_creados(limit=500)
        return context


class MayoresRegistrantesView(AnalyticsViewMixin, ListView):

    model = Registrante
    context_object_name = "registrante"
    template_name = "web/bootstrap-base/registrantes/mayores.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Mayores registrantes'
        context['site_description'] = 'Lista de registrantes con más dominio registrados'

        context['registrantes'] = get_mayores_registrantes(limit=50)
        return context


class RubrosView(AnalyticsViewMixin, ListView):

    model = TagForRegistrante
    context_object_name = "rubros"
    template_name = "web/bootstrap-base/registrantes/rubros.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Rubros o Tags para registrante de dominio'
        context['site_description'] = 'Lista de rubros o Tags para registrante de dominio'

        return context


class RubroView(AnalyticsViewMixin, DetailView):

    model = TagForRegistrante
    context_object_name = "rubro"
    template_name = "web/bootstrap-base/registrantes/rubro.html"

    def get_object(self):
        return TagForRegistrante.objects.get(uid=self.kwargs['uid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_title'] = f'Rubro o Tag {self.object.nombre}'
        context['site_description'] = f'Datos sobre regitrantes etiquetados como {self.object.nombre}'

        # TODO context['ultimos_caidos'] = get_ultimos_caidos(limit=100)
        context['ultimos_registrados'] = get_ultimos_registrados(limit=100, etiqueta=self.object)
        context['mayores_registrantes'] = get_mayores_registrantes(limit=50, etiqueta=self.object)

        webpush = {"group": f'rubro-{self.kwargs["uid"]}'}
        context['webpush'] = webpush
        return context


class AddTagToRegistranteView(View):
    """Vista para agregar un tag existente a un registrante - Solo staff"""

    def post(self, request, uid):
        # Verificar que el usuario es staff
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo usuarios staff pueden realizar esta acción")

        registrante = get_object_or_404(Registrante, uid=uid)
        tag_uid = request.POST.get('tag_uid')

        if tag_uid:
            tag = get_object_or_404(TagForRegistrante, uid=tag_uid)

            # Verificar si ya existe la relación
            if not RegistranteTag.objects.filter(registrante=registrante, tag=tag).exists():
                RegistranteTag.objects.create(registrante=registrante, tag=tag)
                messages.success(request, f'Tag "{tag.nombre}" agregado exitosamente')
            else:
                messages.warning(request, f'El registrante ya tiene el tag "{tag.nombre}"')
        else:
            messages.error(request, 'Debe seleccionar un tag')

        return redirect('registrante', uid=uid)


class CreateAndAddTagView(View):
    """Vista para crear un nuevo tag y agregarlo al registrante - Solo staff"""

    def post(self, request, uid):
        # Verificar que el usuario es staff
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo usuarios staff pueden realizar esta acción")

        registrante = get_object_or_404(Registrante, uid=uid)
        tag_nombre = request.POST.get('tag_nombre', '').strip()

        if tag_nombre:
            # Buscar o crear el tag
            tag, created = TagForRegistrante.objects.get_or_create(nombre=tag_nombre)

            # Verificar si ya existe la relación
            if not RegistranteTag.objects.filter(registrante=registrante, tag=tag).exists():
                RegistranteTag.objects.create(registrante=registrante, tag=tag)
                if created:
                    messages.success(request, f'Tag "{tag_nombre}" creado y agregado exitosamente')
                else:
                    messages.success(request, f'Tag "{tag_nombre}" agregado exitosamente')
            else:
                messages.warning(request, f'El registrante ya tiene el tag "{tag_nombre}"')
        else:
            messages.error(request, 'Debe ingresar un nombre para el tag')

        return redirect('registrante', uid=uid)


class RemoveTagFromRegistranteView(View):
    """Vista para remover un tag de un registrante - Solo staff"""

    def post(self, request, uid):
        # Verificar que el usuario es staff
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo usuarios staff pueden realizar esta acción")

        registrante = get_object_or_404(Registrante, uid=uid)
        tag_uid = request.POST.get('tag_uid')

        if tag_uid:
            tag = get_object_or_404(TagForRegistrante, uid=tag_uid)
            relacion = RegistranteTag.objects.filter(registrante=registrante, tag=tag)

            if relacion.exists():
                relacion.delete()
                messages.success(request, f'Tag "{tag.nombre}" removido exitosamente')
            else:
                messages.warning(request, f'El registrante no tiene el tag "{tag.nombre}"')
        else:
            messages.error(request, 'Tag no especificado')

        return redirect('registrante', uid=uid)


class SubscribeToRegistranteView(View):
    """Create or update a subscription to a registrante - Staff only"""

    def post(self, request, uid):
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo usuarios staff pueden realizar esta acción")

        registrante = get_object_or_404(Registrante, uid=uid)

        ct = ContentType.objects.get_for_model(Registrante)
        target, _ = SubscriptionTarget.objects.get_or_create(
            content_type=ct,
            object_id=registrante.id
        )

        event_types = request.POST.getlist('event_types')
        delivery_mode = request.POST.get('delivery_mode', 'immediate')

        if not event_types:
            messages.error(request, 'Debe seleccionar al menos un tipo de evento')
            return redirect('registrante', uid=uid)

        _, created = UserSubscription.objects.update_or_create(
            user=request.user,
            target=target,
            defaults={
                'event_types': event_types,
                'delivery_mode': delivery_mode,
                'is_active': True
            }
        )

        if created:
            messages.success(request, f'Ahora sigues al registrante {registrante.name}')
        else:
            messages.success(request, f'Suscripción actualizada para {registrante.name}')

        return redirect('registrante', uid=uid)


class UnsubscribeFromRegistranteView(View):
    """Remove a subscription from a registrante - Staff only"""

    def post(self, request, uid):
        if not request.user.is_staff:
            return HttpResponseForbidden("Solo usuarios staff pueden realizar esta acción")

        registrante = get_object_or_404(Registrante, uid=uid)

        ct = ContentType.objects.get_for_model(Registrante)
        target = SubscriptionTarget.objects.filter(
            content_type=ct,
            object_id=registrante.id
        ).first()

        if target:
            deleted, _ = UserSubscription.objects.filter(
                user=request.user,
                target=target
            ).delete()

            if deleted:
                messages.success(request, f'Dejaste de seguir a {registrante.name}')
            else:
                messages.warning(request, 'No tenías una suscripción activa')
        else:
            messages.warning(request, 'No tenías una suscripción activa')

        return redirect('registrante', uid=uid)
