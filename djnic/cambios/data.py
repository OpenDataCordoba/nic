from datetime import timedelta
from django.db.models import Count, Q, DurationField, F, ExpressionWrapper, DateTimeField, IntegerField
from django.db.models.functions import Trunc, Cast
from django.utils import timezone
from dominios.models import STATUS_NO_DISPONIBLE, STATUS_DISPONIBLE
from cambios.models import CampoCambio


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


def get_renovaciones(limit=50):
    """ Dominios que cambia la fecha en que expira """
    cambios = CampoCambio.objects\
        .filter(campo='dominio_expire')\
        .exclude(anterior__exact="")\
        .exclude(nuevo__exact="")\
        .annotate(dnuevo=Cast('nuevo', DateTimeField()))\
        .annotate(danterior=Cast('anterior', DateTimeField()))\
        .annotate(segundos=ExpressionWrapper((F('dnuevo') - F('danterior')) / 86400000000, output_field=IntegerField()))\
        .order_by('-cambio__momento')
        
    return cambios[:limit]
