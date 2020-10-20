from datetime import datetime, timedelta
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from dominios.models import Dominio


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar cambios en los dominios'

    def handle(self, *args, **options):

        dominios = Dominio.objects.filter(
            Q(next_update_priority__isnull=True) | 
            Q(next_update_priority__lt=timezone.now()) 
        )
        
        c = 0
        for dominio in dominios:
            c += 1
            old_up = dominio.next_update_priority
            dominio.calculate_priority()
            self.stdout.write(self.style.SUCCESS(f"{c} {dominio.priority_to_update} {old_up} => {dominio.next_update_priority} {dominio}"))

        self.stdout.write(self.style.SUCCESS(f"{c} processed"))
        