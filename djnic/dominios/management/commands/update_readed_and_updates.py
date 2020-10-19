from datetime import datetime, timedelta
import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q
from dominios.models import Dominio, DNSDominio
from cambios.models import CambiosDominio, CampoCambio


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar cambios en los dominios'

    def handle(self, *args, **options):

        
        dominios = Dominio.objects.filter(
            Q(data_readed__isnull=True) | 
            Q(data_updated__isnull=True) 
        )
        errors = []

        c = 0
        for dominio in dominios:
            c += 1
            if dominio.data_readed is None:
                last_reads = dominio.cambios.order_by('-momento')
                if last_reads.count() == 0:
                    errors.append(f'{dominio} without read records')
                    self.stdout.write(self.style.ERROR(f"{c} {dominio} without read records"))
                    continue

                last_read = last_reads.first()
                dominio.data_readed = last_read.momento
                self.stdout.write(self.style.SUCCESS(f"{c} {dominio} READ "))
            
            if dominio.data_updated is None:
                last_reads = dominio.cambios.filter(have_changes=True).order_by('-momento')
                if last_reads.count() == 0:
                    errors.append(f'{dominio} without changes records')
                    self.stdout.write(self.style.ERROR(f"{c} {dominio} without change records"))
                    continue

                last_read = last_reads.first()
                dominio.data_updated = last_read.momento
                self.stdout.write(self.style.SUCCESS(f"{c} {dominio} CHANGE "))
            dominio.save()

        self.stdout.write(self.style.SUCCESS(f"{c} processed"))
        errors = '\n\t'.join(errors)
        self.stdout.write(self.style.ERROR(f"ERRORS:{errors}"))
