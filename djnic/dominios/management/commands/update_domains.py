from datetime import datetime, timedelta
import logging
from time import sleep
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from dominios.models import Dominio, STATUS_NO_DISPONIBLE, STATUS_DISPONIBLE
from whoare.exceptions import TooManyQueriesError


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualziar datos de dominios'

    def add_arguments(self, parser):
        parser.add_argument('--limit', nargs='?', type=int, default=10000)
        parser.add_argument('--sleep', nargs='?', type=int, default=41)


    def handle(self, *args, **options):
        limit = options['limit']
        dominios = Dominio.objects.all().order_by('-priority_to_update')[:limit]
        print(dominios)
        c = 0
        errors = 0

        sin_cambios = 0
        caidos = 0
        nuevos = 0
        renovados = 0

        for dominio in dominios:
            c += 1
            log_cambios = f'sin_cambios {sin_cambios} caidos {caidos} nuevos {nuevos} renovados {renovados}'
            self.stdout.write(self.style.SUCCESS(f"{c} {errors} {log_cambios} {dominio} expire:{dominio.expire} readed: {dominio.data_readed}"))
            try:
                cambios = Dominio.add_from_whois(domain=dominio.full_domain())
            except TooManyQueriesError:
                self.stdout.write(self.style.SUCCESS(f"WHOIS TooManyQueriesError"))
                errors += 1
                sleep(15)

            if cambios == []:
                sin_cambios += 1
            elif 'estado' in [c['campo'] for c in cambios]:
                for cambio in cambios:
                    if cambio['campo'] == 'estado':
                        if cambio['anterior'] == STATUS_DISPONIBLE:
                            nuevos += 1
                        elif cambio['anterior'] == STATUS_NO_DISPONIBLE:
                            caidos += 1
            elif 'dominio_expire' in [c['campo'] for c in cambios]:
                renovados += 1
            

            sleep(options['sleep'])

            self.stdout.write(self.style.SUCCESS(f" - {dominio.priority_to_update} {dominio.next_update_priority}"))

        self.stdout.write(self.style.SUCCESS(f"{c} processed"))
        