from datetime import datetime, timedelta
import logging
from time import sleep
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from dominios.models import Dominio
from whoare.exceptions import TooManyQueriesError


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualziar datos de dominios'

    def add_arguments(self, parser):
        parser.add_argument('--sleep', nargs='?', type=int, default=10)


    def handle(self, *args, **options):
        f = open('news.txt', 'r')
        doms = f.read()
        f.close()
        dlist = doms.split('\n')
        c = 0
        for dominio in dlist:
            c += 1
            self.stdout.write(self.style.SUCCESS(f"{c} {dominio}"))
            try:
                dom_obj = Dominio.add_from_whois(domain=dominio)
            except TooManyQueriesError:
                dlist.append(dominio)
                self.stdout.write(self.style.SUCCESS(f"WHOIS TooManyQueriesError"))
                sleep(15)
            
            sleep(options['sleep'])

            self.stdout.write(self.style.SUCCESS(f" - {dom_obj}"))

        self.stdout.write(self.style.SUCCESS(f"{c} processed"))
        