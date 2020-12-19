from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.utils import timezone
from dominios.models import Dominio, STATUS_NO_DISPONIBLE


def get_ultimos_registrados(limit=5, de_registrantes_etiquetados=False):
    ultimos = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE)
    
    if de_registrantes_etiquetados:
        ultimos = ultimos.annotate(tags=Count('registrante__tags')).filter(tags__gt=0)

    ultimos = ultimos.order_by('-registered')[:limit]
    return ultimos
