from datetime import timedelta
import logging
from django.db.models import Count, Q, DurationField, F, ExpressionWrapper, DateTimeField, IntegerField
from django.db.models.functions import Trunc, Cast
from django.utils import timezone
from dominios.models import STATUS_NO_DISPONIBLE, STATUS_DISPONIBLE
from cambios.models import CampoCambio
from dnss.models import DNS


logger = logging.getLogger(__name__)


def get_ultimos_caidos(limit=5):
    ultimos_caidos = CampoCambio.objects\
        .filter(campo='estado', anterior=STATUS_NO_DISPONIBLE, nuevo=STATUS_DISPONIBLE)\
        .order_by('-cambio__momento')[:limit]

    return ultimos_caidos


def get_ultimas_transferencias(limit=5):
    """ Dominios que pasan de un registrante a otros
        Pueden no ser transferencias sino sino solo casos
            donde el dominio esta libre poco tiempo y 
            lo registra otra persona. Pasa con dominios valiosos 
        """
    transferencias = CampoCambio.objects\
        .filter(campo='registrant_legal_uid')\
        .exclude(anterior__exact="")\
        .exclude(nuevo__exact="")\
        .order_by('-cambio__momento')

    return transferencias[:limit]


def get_renovaciones(limit=50, solo_fallados=False, solo_hacia_atras=False):
    """ Dominios que cambia la fecha en que expira """
    cambios = CampoCambio.objects\
        .filter(campo='dominio_expire')\
        .exclude(anterior__exact="")\
        .exclude(nuevo__exact="")\
        .annotate(dnuevo=Cast('nuevo', DateTimeField()))\
        .annotate(danterior=Cast('anterior', DateTimeField()))\
        .annotate(tdiff=ExpressionWrapper(F('dnuevo') - F('danterior'), output_field=DurationField()))

    if solo_fallados:
        cambios = cambios.filter(
            Q(tdiff__gt=timedelta(days=370)) | Q(tdiff__lt=timedelta(days=360))
        )

    if solo_hacia_atras:
        cambios = cambios.filter(
            Q(nuevo__lt=F('anterior'))
        )
    
    cambios = cambios.order_by('-cambio__momento')

    return cambios[:limit]


def _get_empresa_from_dominio_dns(dominio):
    dnss = DNS.objects.filter(dominio=dominio)

    if dnss.count() == 0:
        return None
    dns = dnss[0]

    if dns.empresa_regex is None:
        return None
    return dns.empresa_regex.empresa


def get_perdidas_dns(limit=0, days_ago=30):
    """ cambios de DNS """
    logger.info('Get perdidas')
    starts = timezone.now() - timedelta(days=days_ago)
    cambios = CampoCambio.objects\
        .filter(cambio__momento__gt=starts)\
        .filter(campo='DNS1')\
        .exclude(anterior__exact="").distinct()

    if limit > 0:
        cambios = cambios[:limit]

    logger.info(f' - Cambios: {cambios.count()}')
    # detectar empresa anterior y empresa nueva
    final = {}
    c = 0
    cache_dns = {}
    for cambio in cambios:
        c += 1
        if cambio.anterior in cache_dns:
            e1 = cache_dns[cambio.anterior]
        else:
            e1 = _get_empresa_from_dominio_dns(cambio.anterior)

        cache_dns[cambio.anterior] = e1
    
        if e1 is None:
            continue

        if e1.id not in final:
            final[e1.id] = {
                'anterior': e1,
                'perdidas': 0,
                'migraciones': {}
            }

        final[e1.id]['perdidas'] += 1
        logger.info(f' - {c} {e1.nombre}: {final[e1.id]["perdidas"]}')

        if cambio.nuevo in cache_dns:
            e2 = cache_dns[cambio.nuevo]
        else:
            e2 = _get_empresa_from_dominio_dns(cambio.nuevo)

        if e2.id == e1.id:
            # al final no era una pérdida
            final[e1.id]['perdidas'] -= 1
        else:
            e2id = 0 if e2 is None else e2.id
            if e2id not in final[e1.id]['migraciones']:
                final[e1.id]['migraciones'][e2id] = {
                    'empresa': e2,
                    'total': 0
                }
            final[e1.id]['migraciones'][e2id]['total'] += 1

    return final
