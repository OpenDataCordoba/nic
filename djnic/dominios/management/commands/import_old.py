from datetime import datetime
import logging
import mysql.connector
import pytz
# from sshtunnel import SSHTunnelForwarder
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dominios.models import Dominio, DNSDominio, STATUS_DISPONIBLE, STATUS_NO_DISPONIBLE
from zonas.models import Zona
from registrantes.models import Registrante
from dnss.models import DNS


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar dominios'

    def add_arguments(self, parser):
        parser.add_argument('--limit', nargs='?', type=int, default=0)
        parser.add_argument('--offset', nargs='?', type=int, default=0)


    def handle(self, *args, **options):
        limit = options['limit']
        offset = options['offset']

        tz = pytz.timezone('America/Argentina/Cordoba')

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
        cursor.execute("SET SESSION MAX_EXECUTION_TIME=100000000;")
        
        query = 'Select * from dominios order by lastUpdated '
        if limit > 0:
            query += f'limit {limit}'
        if offset > 0:
            query += f'offset {offset} rows'
        query += ';'
        
        self.stdout.write(self.style.SUCCESS(f'Query {query}'))
        cursor.execute(query)

        """ sample data 
        "id", "dominio",  "estado",       "lastUpdated",         "desde",               "hasta",              "registrante",        "reg_documento", "DNS1",                 "DNS2","DNS3","DNS4","DNS5", "dominio_changed",     "persona_changed",     "persona_created",     "server_created"
        "187","a.com.ar", "no disponible","2020-02-29 23:24:53", "2014-03-03 00:00:00", "2021-03-03 00:00:00","PINEDA SERGIO RUBEN","20180552449",   "ns2.sedoparking.com",  "ns1.sedoparking.com",,,,,   "2020-02-17 18:28:07", "2020-02-12 17:34:04", "2013-08-20 00:00:00", "2016-07-01 01:16:14"
        "188","e.com.ar", "disponible",   "2017-07-15 13:29:56", "0000-00-00 00:00:00", "0000-00-00 00:00:00",                                                                                            "0000-00-00 00:00:00", "0000-00-00 00:00:00", "0000-00-00 00:00:00", "0000-00-00 00:00:00"

        """
        c = 0
        nuevos_dominios = 0
        nuevos_registrantes = 0
        skipped = 0
        for d in cursor:
            c += 1
            parts = d['dominio'].lower().strip().split('.')
            base_name = parts[0]
            zone = '.'.join(parts[1:])

            if d['lastUpdated'] is None:
                skipped += 1
                continue            
            reg_name = d['registrante'].lower().strip()
            reg_uid = d['reg_documento'].lower().strip()
            
            self.stdout.write(self.style.SUCCESS(f"{c} Procesndo dominio {d['lastUpdated']} {base_name} {zone} {d['estado']} {reg_name}"))
            
            zona, created = Zona.objects.get_or_create(nombre=zone)

            dominio, created = Dominio.objects.get_or_create(zona=zona, nombre=base_name)
            if created:
                nuevos_dominios += 1

            dominio.uid_anterior = d['id']
            dominio.data_updated = tz.localize(d["lastUpdated"], is_dst=True)
            if d["dominio_changed"] is not None:
                dominio.changed = tz.localize(d["dominio_changed"], is_dst=True)

            if d['estado'] == "no disponible":
                dominio.estado = STATUS_NO_DISPONIBLE
            
                if d["desde"] is not None:
                    dominio.registered = tz.localize(d["desde"], is_dst=True)
                
                if d["hasta"] is not None:
                    dominio.expire = tz.localize(d["hasta"], is_dst=True)
            
                registrante, created = Registrante.objects.get_or_create(legal_uid=reg_uid)
                if created:
                    nuevos_registrantes += 1

                if d['persona_changed'] is not None:
                    registrante.created = tz.localize(d["persona_changed"], is_dst=True)
                if d['persona_created'] is not None:
                    registrante.changed = tz.localize(d["persona_created"], is_dst=True)
                
                registrante.name = reg_name  # necesito laultima version de su nombre, por eso debo ordenar bien
                registrante.save()

                dominio.registrante = registrante
            else:
                dominio.estado = STATUS_DISPONIBLE
                
                if reg_name is not None and reg_name != '':
                    raise Exception('Registrante pero dominio en estado no esperado')
                if d["desde"] is not None:
                    raise Exception('Valor no esperado')
                if d["hasta"] is not None:
                    raise Exception('Valor no esperado')
            dominio.save()

            orden = 1
            for ns in [d["DNS1"], d["DNS2"], d["DNS3"], d["DNS4"], d["DNS5"]]:
                if ns is not None and ns != '':
                    ns = ns.lower().strip()
                    parts = ns.split()
                    dns, created = DNS.objects.get_or_create(dominio=parts[0])
                    if dns in [d.dns for d in dominio.dnss.all()]:
                        continue
                    DNSDominio.objects.create(dominio=dominio, dns=dns, orden=orden)
                    orden += 1

        cursor.close()
        connection.close()

        # server.stop()

        self.stdout.write(self.style.SUCCESS(f"{c} procesados, {nuevos_dominios} nuevos dominios. Nuevos registrantes: {nuevos_registrantes}. Skipped: {skipped}"))
