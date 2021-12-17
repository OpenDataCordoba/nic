from datetime import datetime
import logging
import mysql.connector
import pytz
# from sshtunnel import SSHTunnelForwarder
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dominios.models import Dominio, DNSDominio
from zonas.models import Zona
from registrantes.models import Registrante
from dnss.models import DNS


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar dominiod'

    def handle(self, *args, **options):

        DNSDominio.objects.all().delete()
        Dominio.objects.all().delete()
        DNS.objects.all().delete()
        Registrante.objects.all().delete()
        Zona.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("DELETED"))
