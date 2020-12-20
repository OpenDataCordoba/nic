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
