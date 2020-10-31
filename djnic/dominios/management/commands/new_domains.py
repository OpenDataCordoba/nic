from datetime import datetime, timedelta
import logging
from time import sleep
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from dominios.models import Dominio


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualizar datos de dominios'

    def add_arguments(self, parser):
        parser.add_argument('--sleep', nargs='?', type=int, default=41)

    def handle(self, *args, **options):
        f = open('news.txt', 'r')
        doms = f.read()
        f.close()
        dlist = doms.split('\n')
        c = 0
        errors = 0
        skipped = 0
        for dominio in dlist:
            c += 1
            self.stdout.write(self.style.SUCCESS(f"{c} [{errors}] [{skipped}] {dominio}"))
            dom_obj = Dominio.add_from_whois(domain=dominio, just_new=True)
            if dom_obj is None:
                dlist.append(dominio)
                errors += 1
                self.stdout.write(self.style.SUCCESS(f"WHOIS TooManyQueriesError Error"))
                sleep(15)
            
            if dom_obj == True:
                skipped += 1
                continue
            
            sleep(options['sleep'])

            self.stdout.write(self.style.SUCCESS(f" - {dominio} {dom_obj}"))

        self.stdout.write(self.style.SUCCESS(f"{c} processed"))
        