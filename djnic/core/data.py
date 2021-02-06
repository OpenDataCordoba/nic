from django.db.models import Q
from dominios.models import Dominio
from registrantes.models import Registrante
from dnss.models import Empresa, DNS
from cache_memoize import cache_memoize
from django.conf import settings


from mensajes.models import MensajeDestinado


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_search_results(query):
    res = {}
    res['dominios'] = Dominio.objects.filter(nombre__icontains=query).order_by('nombre')[:50]
    res['registrantes'] = Registrante.objects.filter(
        Q(name__icontains=query) | Q(legal_uid__icontains=query)
    ).order_by('name')[:50]
    res['hostings'] = Empresa.objects.filter(nombre__icontains=query).order_by('nombre')[:50]
    res['dnss'] = DNS.objects.filter(dominio__icontains=query).order_by('dominio')[:50]

    return res


def get_messages(user):
    """ Obtener todos los mensajes del usuario para la lista de novedades """
    if user.is_authenticated:
        mensajes = MensajeDestinado.objects.filter(destinatario=user).exclude(estado=MensajeDestinado.DELETED)
    else:
        mensajes = []
    return mensajes


def get_notifications(user):
    """ Obtener los mensajes no leidos del usuario """
    if user.is_authenticated:
        mensajes = MensajeDestinado.objects.filter(
            destinatario=user,
            estado=MensajeDestinado.CREATED
        )
    else:
        mensajes = []
    return mensajes
