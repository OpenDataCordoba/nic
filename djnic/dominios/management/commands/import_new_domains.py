from datetime import datetime, timedelta
import logging
from time import sleep
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from whoare.whoare import WhoAre
from dominios.models import Dominio, PreDominio
from zonas.models import Zona


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar archivos de texto con posibles dominios nuevos a la base'

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str, help='Path del archivo con los datos (lista simple de texto')
        parser.add_argument('--priority', nargs='?', type=int, default=50)

    def handle(self, *args, **options):
        f = open(options['path'], 'r')
        doms = f.read()
        f.close()
        dlist = doms.split('\n')
        c = 0
        skipped = 0
        for dominio in dlist:
            dominio = dominio.strip().lower()
            c += 1
            self.stdout.write(self.style.SUCCESS(f"{c} [{skipped}] {dominio}"))
            # ver si ya existe en la base
            wa = WhoAre()
            domain_name, zone = wa.detect_zone(dominio)
            zona = Zona.objects.get(nombre=zone)

            dominios = Dominio.objects.filter(nombre=domain_name, zona=zona)
            if dominios.count() > 0:
                skipped += 1
                continue

            _, created = PreDominio.objects.get_or_create(dominio=dominio, priority=options['priority'])
            if not created:
                skipped += 1
            
        self.stdout.write(self.style.SUCCESS(f"DONE. {c} processed {skipped} skipped"))
        