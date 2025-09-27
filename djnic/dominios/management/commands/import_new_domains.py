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

            pd, created = PreDominio.objects.get_or_create(dominio=dominio)
            # ID=0 si ya existe como dominio
            if not created or pd.id == 0:
                skipped += 1

            pd.priority=options['priority']
            pd.save()

        self.stdout.write(self.style.SUCCESS(f"DONE. {c} processed {skipped} skipped"))
