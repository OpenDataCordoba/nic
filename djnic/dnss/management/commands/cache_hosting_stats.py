from django.core.management.base import BaseCommand
from django.core.cache import cache
from dnss.data import get_hosting_usados, get_orphan_dns, get_dominios_sin_dns_count
from cambios.data import get_perdidas_dns


class Command(BaseCommand):
    help = 'Pre-compute and cache hosting statistics'

    def handle(self, *args, **options):
        self.stdout.write('Starting hosting statistics cache update...')

        # Cache main hostings data (limit 250)
        self.stdout.write('Caching main hostings data...')
        get_hosting_usados(limit=250, use_cache=False)

        # Cache 30-day hostings data (limit 100)
        self.stdout.write('Caching 30-day hostings data...')
        get_hosting_usados(days_ago=30, limit=100, use_cache=False)

        # Cache orphan DNS data (limit 250)
        self.stdout.write('Caching orphan DNS data...')
        get_orphan_dns(limit=250, use_cache=False)

        # Cache domains without DNS count
        self.stdout.write('Caching count of domains without DNS...')
        get_dominios_sin_dns_count(use_cache=False)

        # Cache perdidas DNS data
        self.stdout.write('Caching perdidas DNS data...')
        perdidas = get_perdidas_dns(days_ago=30)
        cache.set('perdidas_dns_30', perdidas, timeout=86400)

        self.stdout.write(
            self.style.SUCCESS('Successfully cached hosting statistics')
        )
