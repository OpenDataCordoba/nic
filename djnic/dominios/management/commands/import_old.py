import logging
import mysql.connector
# from sshtunnel import SSHTunnelForwarder
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dominios.models import Dominio
from zonas.models import Zona
from registrantes.models import Registrante
from dnss.models import DNS


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar dominiod'

    def add_arguments(self, parser):
        parser.add_argument('--limit', nargs='?', type=int, default=100)

    def handle(self, *args, **options):
        limit = options['limit']

        # create a SSH tunnel
        # https://support.cloud.engineyard.com/hc/en-us/articles/205408088-Access-Your-Database-Remotely-Through-an-SSH-Tunnel
        # ssh -p XXX -L 3307:REMOTE_HOST:3306 user@REMOTE_HOST
        # self.stdout.write(self.style.SUCCESS(f'Tunneling to {settings.OLD_SSH_HOST}'))
        
        # # https://pypi.org/project/sshtunnel/
        # server = SSHTunnelForwarder(
        #     (settings.OLD_SSH_HOST, settings.OLD_SSH_PORT),
        #     ssh_username=settings.OLD_SSH_USER,
        #     ssh_password=settings.OLD_SSH_PASS,
        #     remote_bind_address=('127.0.0.1', 3306)
        # )

        # server.start()

        # self.stdout.write(self.style.SUCCESS(f'Tunnel OK on port {server.local_bind_port}'))
        
        logger.info('Connecting DB')
        connection = mysql.connector.connect(
            user=settings.OLD_DB_USER,
            password=settings.OLD_DB_PASS,
            host='127.0.0.1',
            database=settings.OLD_DB_NAME,
            port=3307  # I create a SSH tunnel here
            )


        # https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-select.html
        cursor = connection.cursor(dictionary=True)  # sin el dictionary=True son tuplas sin nombres de campo
        
        query = f'Select * from dominios limit {limit};'
        
        self.stdout.write(self.style.SUCCESS(f'Query {query}'))
        cursor.execute(query)

        """ sample data 
        "id", "dominio",  "estado",       "lastUpdated",         "desde",               "hasta",              "registrante",        "reg_documento", "DNS1",                 "DNS2","DNS3","DNS4","DNS5", "dominio_changed",     "persona_changed",     "persona_created",     "server_created"
        "187","a.com.ar", "no disponible","2020-02-29 23:24:53", "2014-03-03 00:00:00", "2021-03-03 00:00:00","PINEDA SERGIO RUBEN","20180552449",   "ns2.sedoparking.com",  "ns1.sedoparking.com",,,,,   "2020-02-17 18:28:07", "2020-02-12 17:34:04", "2013-08-20 00:00:00", "2016-07-01 01:16:14"
        "188","e.com.ar", "disponible",   "2017-07-15 13:29:56", "0000-00-00 00:00:00", "0000-00-00 00:00:00",                                                                                            "0000-00-00 00:00:00", "0000-00-00 00:00:00", "0000-00-00 00:00:00", "0000-00-00 00:00:00"

        """
        c = 0
        nuevos_dominios = 0
        for d in cursor:
            c += 1
            parts = d['dominio'].split('.')
            base_name = parts[0]
            zone = '.'.join(parts[1:])
            zona, created = Zona.objects.get_or_create(nombre=zone)
            dominio, created = Dominio.objects.get_or_create(zona=zona, nombre=base_name)
            if created:
                nuevos_dominios += 1

            self.stdout.write(self.style.SUCCESS(f"\tDominio {dominio}"))

        cursor.close()
        connection.close()

        # server.stop()

        self.stdout.write(self.style.SUCCESS(f"{c} procesados, {nuevos_dominios} nuevos dominios"))
        