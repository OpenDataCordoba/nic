from django.db.models import Q
from dominios.models import Dominio
from registrantes.models import Registrante
from dnss.models import Empresa, DNS
from zonas.models import Zona
from cache_memoize import cache_memoize
from django.conf import settings


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_search_results(query):
    res = {
        'exacto': [],
        'parecidos': [],
        'dominios': [],
        'registrantes': [],
        'hostings': [],
        'dnss': [],
    }
    # no permitir muy cortas
    if len(query) < 4:
        return res
    # no permitir muy largas
    if len(query) > 150:
        return res
    query = query.lower()
    if query.endswith('.ar'):
        # Estamos buscando un dominio con la zona completa
        # esto es dominio.nombre + dominio.zona.nombre
        partes = query.split('.')
        dominio_nombre = partes[0]
        zona_nombre = '.'.join(partes[1:])
        zona = Zona.objects.filter(nombre=zona_nombre).first()
        if zona:
            # primero que todo el exacto
            exact_dom = Dominio.objects.filter(
                nombre=dominio_nombre,
                zona=zona
            ).first()
            if exact_dom:
                res['exacto'] = [exact_dom]

        if len(dominio_nombre) > 3:
            res['parecidos'] = Dominio.objects.filter(nombre__icontains=dominio_nombre).order_by('nombre')[:250]

    else:
        res['dominios'] = Dominio.objects.filter(nombre__icontains=query).order_by('nombre')[:250]
        res['registrantes'] = Registrante.objects.filter(
            Q(name__icontains=query) | Q(legal_uid__icontains=query)
        ).order_by('name')[:250]
        res['hostings'] = Empresa.objects.filter(nombre__icontains=query).order_by('nombre')[:250]

    res['dnss'] = DNS.objects.filter(dominio__icontains=query).order_by('dominio')[:250]

    return res
