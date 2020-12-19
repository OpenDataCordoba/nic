from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.utils import timezone
from dominios.models import Dominio


def get_ultimos_dominios_actualizados_por_grupo(grupo, days_ago=30):
    starts = timezone.now() - timedelta(days=days_ago)
    dominios = Dominio.objects.filter(
        data_updated__gt=starts,
        zona__grupos__grupo=grupo
        )
    
    grouped = dominios.annotate(dia_updated=Trunc('data_updated', 'day'))\
        .order_by('-dia_updated')\
        .values('dia_updated')\
        .annotate(total=Count('dia_updated'))
    
    return grouped


def get_ultimos_dominios_actualizados_por_zona(zona, days_ago=30):
    starts = timezone.now() - timedelta(days=days_ago)
    dominios = Dominio.objects.filter(
        data_updated__gt=starts,
        zona=zona)
    
    grouped = dominios.annotate(dia_updated=Trunc('data_updated', 'day'))\
        .order_by('-dia_updated')\
        .values('dia_updated')\
        .annotate(total=Count('dia_updated'))
    
    return grouped