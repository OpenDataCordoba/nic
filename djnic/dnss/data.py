from datetime import timedelta
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone
from dnss.models import Empresa, DNS
from dominios.models import Dominio
from cache_memoize import cache_memoize
from django.conf import settings


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_hosting_usados(days_ago=0, limit=5, use_cache=True):
    # Generate cache key based on parameters
    cache_key = f'hostings_{days_ago}_{limit}'

    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

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

    # Always cache the result when we calculate it
    cache.set(cache_key, hostings, timeout=86400)  # 24 hours

    return hostings


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_dominios_from_hosting(hosting, limit=5, use_cache=True):
    cache_key = f'hosting_dominios_{hosting.uid}_{limit}'

    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

    dominios = Dominio.objects.filter(
        dnss__dns__empresa_regex__empresa=hosting
    ).distinct().order_by('-registered')

    if limit > 0:
        dominios = dominios[:limit]

    # Always cache the result when we calculate it
    cache.set(cache_key, dominios, timeout=86400)  # 24 hours

    return dominios


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_orphan_dns(limit=5, use_cache=True):
    cache_key = f'orphan_dns_{limit}'

    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

    orphans = DNS.objects.filter(
        empresa_regex__isnull=True
    ).annotate(
        total_dominios=Count('dominios', filter=Q(dominios__orden=1))
    ).order_by('-total_dominios')

    result = orphans[:limit]

    # Always cache the result when we calculate it
    cache.set(cache_key, result, timeout=86400)  # 24 hours

    return result


@cache_memoize(settings.GENERAL_CACHE_SECONDS)
def get_dominios_sin_dns_count(use_cache=True):
    cache_key = 'dominios_sin_dns_count'

    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

    from dominios.data import dominios_sin_dns
    count = dominios_sin_dns(limit=0).count()

    # Always cache the result when we calculate it
    cache.set(cache_key, count, timeout=86400)  # 24 hours

    return count
