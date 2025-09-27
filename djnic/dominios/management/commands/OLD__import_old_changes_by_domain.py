from datetime import datetime
import logging
import mysql.connector
import pytz
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dominios.models import Dominio, DNSDominio
from cambios.models import CambiosDominio, CampoCambio


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar cambios en los dominios'

    def handle(self, *args, **options):

        # limpiar los incompletos
        CambiosDominio.objects.filter(dominio__changes_migrated=1).delete()

        tz = pytz.timezone('America/Argentina/Cordoba')

        logger.info('Connecting DB')
        connection = mysql.connector.connect(
            user=settings.OLD_DB_USER,
            password=settings.OLD_DB_PASS,
            host='127.0.0.1',
            database=settings.OLD_DB_NAME,
            port=3307  # I create a SSH tunnel here
            )

        cursor = connection.cursor(dictionary=True)  # sin el dictionary=True son tuplas sin nombres de campo
        cursor.execute("SET SESSION MAX_EXECUTION_TIME=100000000;")

        tables = ['cambios_2011', 'cambios_2012', 'cambios_2013', 'cambios_2014',
                  'cambios_2015', 'cambios_2016', 'cambios_2017', 'cambios_2018',
                  'cambios_2019', 'cambios']

        dominios = Dominio.objects.filter(changes_migrated=0)

        for dominio in dominios:
            # para cada dominio ir a todas las tablas con cambios
            dominio.changes_migrated = 1
            dominio.save()
            for table in tables:
                main_cambio = None  # solo se crea si hay que ponerle
                self.stdout.write(self.style.SUCCESS(f'Table {table}'))

                query = f'''SELECT * FROM {table}
                            where idDominio = {dominio.uid_anterior}
                            order by fecha ASC;'''

                cursor.execute(query)

                c = 0
                for cambio in cursor:
                    c += 1
                    self.stdout.write(self.style.SUCCESS(f"\t {c} Procesndo cambio {cambio['campo']} from {cambio['anterior']} to {cambio['nuevo']}"))
                    momento = tz.localize(cambio['fecha'], is_dst=True)
                    if main_cambio is None:
                        main_cambio = CambiosDominio.objects.create(dominio=dominio, momento=momento)
                    else:
                        # ver si estan muy separados o no
                        diff = momento - main_cambio.momento
                        if diff.total_seconds() > 3600:
                            # crear uno nuevo
                            main_cambio = CambiosDominio.objects.create(dominio=dominio, momento=momento)

                    CampoCambio.objects.create(
                        cambio=main_cambio,
                        campo=cambio['campo'],
                        anterior=cambio['anterior'],
                        nuevo=cambio['nuevo']
                        )


                self.stdout.write(self.style.SUCCESS(f'Finished Table {table}'))

            dominio.changes_migrated = 2
            dominio.save()

        cursor.close()
        connection.close()

        # server.stop()

        self.stdout.write(self.style.SUCCESS(f"{c} procesados."))
