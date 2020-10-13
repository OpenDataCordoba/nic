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
        # 'cambios_2011', 
        tables = ['cambios_2012', 'cambios_2013', 'cambios_2014',
                  'cambios_2015', 'cambios_2016', 'cambios_2017', 'cambios_2018',
                  'cambios_2019', 'cambios']

        for table in tables:
            
            self.stdout.write(self.style.SUCCESS(f'Table {table}'))
        
            query = f'''SELECT * FROM {table}
                        order by id ASC;'''
    
            cursor.execute(query)

            c = 0
            last_id_dominio = None
            main_cambio = None
            for cambio in cursor:
                c += 1
                if last_id_dominio is None or last_id_dominio != cambio['idDominio']:
                    dominios = Dominio.objects.filter(uid_anterior=cambio['idDominio'])
                    if dominios.count() == 0:
                        self.stdout.write(self.style.ERROR(f"IGNORED idDominio {cambio['idDominio']}"))
                        continue
                    elif dominios.count() > 1:
                        raise('WHAT!')
                    last_id_dominio = cambio['idDominio']
                    dominio = dominios[0]    
                    main_cambio = None
                
                self.stdout.write(self.style.SUCCESS(f"[{table}]:{c} Procesndo cambio {cambio['campo']} from {cambio['anterior']} to {cambio['nuevo']}"))
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
    
        cursor.close()
        connection.close()

        # server.stop()

        self.stdout.write(self.style.SUCCESS(f"{c} procesados, {nuevos_dominios} nuevos dominios. Nuevos registrantes: {nuevos_registrantes}. Skipped: {skipped}"))
