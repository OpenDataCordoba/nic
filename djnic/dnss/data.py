from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.utils import timezone
from dnss.models import Empresa
from dominios.models import Dominio


def get_hosting_usados(days_ago=0, limit=5):

    # Empresas de hosting más usadas
    hostings = Empresa.objects.all()

    if days_ago > 0:
        starts = timezone.now() - timedelta(days=days_ago)
        hostings = hostings.filter(
            regexs__nameservers__dominios__dominio__registered__gt=starts
        )

    hostings = hostings.annotate(
        total_dominios=Count('regexs__nameservers__dominios', filter=Q(regexs__nameservers__dominios__orden=1))
    ).order_by('-total_dominios')[:limit]

    return hostings


def get_dominios_from_hosting(hosting, limit=5):
    dominios = Dominio.objects.filter(
        dnss__dns__empresa_regex__empresa=hosting
    ).order_by('-registered')[:limit]

    return dominios
