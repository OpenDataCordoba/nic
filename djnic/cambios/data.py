from datetime import timedelta
from django.db.models import Count, Q, DurationField, F, ExpressionWrapper, DateTimeField, IntegerField
from django.db.models.functions import Trunc, Cast
from django.utils import timezone
from dominios.models import STATUS_NO_DISPONIBLE, STATUS_DISPONIBLE
from cambios.models import CampoCambio
from dnss.models import DNS


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


def get_perdidas_dns(limit=0, days_ago=30):
    """ cambios de DNS """
    starts = timezone.now() - timedelta(days=days_ago)
    cambios = CampoCambio.objects\
        .filter(cambio__momento__gt=starts)\
        .filter(campo='DNS1')\
        .exclude(anterior__exact="")

    cambios = cambios.order_by('-cambio__momento')

    if limit > 0:
        cambios = cambios[:limit]

    # detectar empresa anterior y empresa nueva
    final = {}
    for cambio in cambios:
        dnss = DNS.objects.filter(dominio=cambio.anterior)
        if dnss.count() == 0:
            # TODO ver que pasa, no debería pasar
            continue
        dns = dnss[0]
        # Me interesan solo los que tienen una empresa
        if dns.empresa_regex is None:
            continue
        e1 = dns.empresa_regex.empresa
        if e1.id not in final:
            final[e1.id] = {
                'anterior': e1,
                'perdidas': 0,
                'migraciones': {}
            }

        final[e1.id]['perdidas'] += 1

        if cambio.nuevo == '':
            continue
        dnss = DNS.objects.filter(dominio=cambio.nuevo)
        if dnss.count() == 0:
            # TODO ver que pasa, no debería pasar
            continue
        dns = dnss[0]
        if dns.empresa_regex is None:
            continue
        e2 = dns.empresa_regex.empresa
        if e2 == e1:
            # al final no era una pérdida
            final[e1.id]['perdidas'] -= 1
        else:
            if e2.id not in final[e1.id]['migraciones']:
                final[e1.id]['migraciones'][e2.id] = {
                    'empresa': e2,
                    'total': 0
                }
            final[e1.id]['migraciones'][e2.id]['total'] += 1

    return final
