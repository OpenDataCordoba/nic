from datetime import datetime, timedelta
import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q
from dominios.models import Dominio, DNSDominio, STATUS_DISPONIBLE
from cambios.models import CambiosDominio, CampoCambio


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Eliminar dominios que estan libres y nunca detectamos como registrados'
    def add_arguments(self, parser):
        parser.add_argument('--delete', nargs='?', default=False, type=bool, help='Really delete, not only show')
    

    def handle(self, *args, **options):
    
        dominios = Dominio.objects.all()
        errors = []

        to_delete = []
        c = 0
        for dominio in dominios:
            c += 1
            if dominio.estado == STATUS_DISPONIBLE:
                if dominio.cambios.filter(have_changes=True).count() == 0:
                    to_delete.append(dominio)
                    logger.info(f'{c} delete {dominio}')
            
        self.stdout.write(self.style.SUCCESS(f"{c} processed {len(to_delete)} to be deleted"))
        if options['delete']:
            for d in to_delete:
                d.delete()
        
        errors = '\n\t'.join(errors)
        self.stdout.write(self.style.ERROR(f"ERRORS:{errors}"))
