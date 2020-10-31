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
            dom_obj, error, changes = Dominio.add_from_whois(domain=dominio, just_new=True)
            self.stdout.write(self.style.SUCCESS(f"{c} [{errors}] [{skipped}] {dominio}: {dom_obj}, {error}, {changes}"))
            
            if not dom_obj:
                dlist.append(dominio)
                errors += 1
                self.stdout.write(self.style.SUCCESS(f"Error {error}"))
                sleep(15)
            else:
                skipped += 1
                if error == 'Already exists':
                    continue
            
            sleep(options['sleep'])
            self.stdout.write(self.style.SUCCESS(f" - cambios {changes}"))

        self.stdout.write(self.style.SUCCESS(f"DONE. {c} processed"))
        