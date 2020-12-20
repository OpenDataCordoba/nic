from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.utils import timezone
from dominios.models import Dominio, STATUS_NO_DISPONIBLE


def get_ultimos_registrados(limit=5, de_registrantes_etiquetados=False, etiqueta=None):
    ultimos = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE)

    if de_registrantes_etiquetados:
        ultimos = ultimos.annotate(tags=Count('registrante__tags')).filter(tags__gt=0)

    if etiqueta is not None:
        ultimos = ultimos.filter(registrante__tags__tag=etiqueta)

    ultimos = ultimos.order_by('-registered')[:limit]
    return ultimos


def get_primeros_registrados(limit=5, de_registrantes_etiquetados=False, etiqueta=None):
    ultimos = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE, registered__isnull=False)

    if de_registrantes_etiquetados:
        ultimos = ultimos.annotate(tags=Count('registrante__tags')).filter(tags__gt=0)

    if etiqueta is not None:
        ultimos = ultimos.filter(registrante__tags__tag=etiqueta)

    ultimos = ultimos.order_by('registered')[:limit]
    return ultimos


def get_judicializados(limit=50, days_ago=300):
    """ dominios que vencieron hace mucho pero no cayeron
        TODO ver si el registrante "NIC Juridicos" es mejor """
    starts = timezone.now() - timedelta(days=days_ago)
    dominios = Dominio.objects.filter(
        estado=STATUS_NO_DISPONIBLE,
        expire__lt=starts)

    dominios = dominios.order_by('expire')[:limit]
    return dominios
