from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.utils import timezone
from registrantes.models import Registrante


def get_ultimos_reg_creados(limit=5, de_registrantes_etiquetados=False, etiqueta=None):
    ultimos = Registrante.objects.order_by('-created')[:limit]
    return ultimos


def get_primeros_reg_creados(limit=5, de_registrantes_etiquetados=False, etiqueta=None):
    ultimos = Registrante.objects.order_by('created')[:limit]
    return ultimos


def get_mayores_registrantes(limit=5, de_registrantes_etiquetados=False, etiqueta=None):
    """ registrantes con más dominios """
    regs = Registrante.objects.annotate(total_dominios=Count('dominios'))

    if de_registrantes_etiquetados:
        regs = regs.annotate(total_tags=Count('tags')).filter(total_tags__gt=0)

    if etiqueta is not None:
        regs = regs.filter(tags__tag=etiqueta)

    regs = regs.order_by('-total_dominios')
    return regs[:limit]
