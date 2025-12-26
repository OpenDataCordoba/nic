from datetime import timedelta
from django.db.models import Count
from django.utils import timezone
from dominios.models import Dominio, STATUS_NO_DISPONIBLE
from cache_memoize import cache_memoize
from django.conf import settings


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_ultimos_registrados(limit=5, de_registrantes_etiquetados=False, etiqueta=None, zona=None):
    ultimos = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE)

    if zona:
        ultimos = ultimos.filter(zona=zona)

    if de_registrantes_etiquetados:
        ultimos = ultimos.annotate(tags=Count('registrante__tags')).filter(tags__gt=0)

    if etiqueta is not None:
        ultimos = ultimos.filter(registrante__tags__tag=etiqueta)

    ultimos = ultimos.order_by('-registered')[:limit]
    return ultimos


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_primeros_registrados(limit=5, de_registrantes_etiquetados=False, etiqueta=None):
    ultimos = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE, registered__isnull=False)

    if de_registrantes_etiquetados:
        ultimos = ultimos.annotate(tags=Count('registrante__tags')).filter(tags__gt=0)

    if etiqueta is not None:
        ultimos = ultimos.filter(registrante__tags__tag=etiqueta)

    ultimos = ultimos.order_by('registered')[:limit]
    return ultimos


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_judicializados(limit=50, days_ago=300):
    """ dominios que vencieron hace mucho pero no cayeron
        TODO ver si el registrante "NIC Juridicos" es mejor """
    starts = timezone.now() - timedelta(days=days_ago)
    dominios = Dominio.objects.filter(
        estado=STATUS_NO_DISPONIBLE,
        expire__lt=starts)

    dominios = dominios.order_by('expire')[:limit]
    return dominios


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_futuros(limit=5, de_registrantes_etiquetados=False, etiqueta=None):
    """ Dominios que vencen más en el futuro """
    starts = timezone.now() + timedelta(days=366)
    ultimos = Dominio.objects.filter(expire__isnull=False).order_by('-expire').filter(expire__gt=starts)[:limit]
    return ultimos


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def dominios_sin_dns(limit=5):
    # agregar los que no tienen DNS
    dominios = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE, dnss__isnull=True)

    if limit > 0:
        dominios = dominios[:limit]

    return dominios


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_por_caer(limit=5, de_registrantes_etiquetados=False, etiqueta=None):

    # TODO esto es para Argentina. Cada pais deberá tener sus reglas
    starts = timezone.now() - timedelta(days=44)
    ends = timezone.now() - timedelta(days=47)
    dominios = Dominio.objects.filter(
        estado=STATUS_NO_DISPONIBLE,
        expire__lt=starts,
        expire__gt=ends
    )

    if de_registrantes_etiquetados:
        dominios = dominios.annotate(tags=Count('registrante__tags')).filter(tags__gt=0)

    if etiqueta is not None:
        dominios = dominios.filter(registrante__tags__tag=etiqueta)

    dominios = dominios.order_by('registered')
    if limit > 0:
        dominios = dominios[:limit]

    return dominios
