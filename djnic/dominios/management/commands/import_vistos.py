from datetime import datetime, timedelta
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

    def add_arguments(self, parser):
        parser.add_argument('--offset', nargs='?', type=int, default=0)
        parser.add_argument('--chunks', nargs='?', type=int, default=5000)
        parser.add_argument('--limit', nargs='?', type=int, default=15522038)

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
        
        # tables = ['cambios_2011', 'cambios_2012', 'cambios_2013', 'cambios_2014',
        #           'cambios_2015', 'cambios_2016', 'cambios_2017', 'cambios_2018',
        #           'cambios_2019', 'cambios']

        offset = options['offset']
        chunks = options['chunks']
        limit = options['limit']
        
        c = offset
        errors = []

        for n in range(0, 130000000, chunks):

            if offset > limit:
                break
            
            query = f'''SELECT * FROM dominio_visto order by id ASC limit {chunks} offset {offset};'''

            cursor.execute(query)

            # preparar la pagina que sigue 
            offset += chunks 
            
            for cambio in cursor:
                c += 1
                if cambio['momento'] is None:
                    continue
                momento = tz.localize(cambio['momento'], is_dst=True)
                max_diff = timedelta(hours=12)
                desde = momento - max_diff
                hasta = momento + max_diff

                dominios = Dominio.objects.filter(uid_anterior=cambio['idDominio'])
                if dominios.count() == 0:
                    continue
                dominio = dominios[0]

                # ver si estan muy separados o no
                closest_changes = CambiosDominio.objects.filter(
                    dominio=dominio,
                    momento__gt=desde,
                    momento__lt=hasta)
                
                if closest_changes.count() == 0:
                    # crear uno nuevo
                    main_cambio = CambiosDominio.objects.create(
                        dominio=dominio,
                        momento=momento,
                        have_changes=False)
                    self.stdout.write(self.style.SUCCESS(f'{c} CREATE Visto {dominio} {momento}'))
                else:
                    cc = closest_changes[0]
                    skipped = f'{c} SKIP {momento} because we have another change for {dominio} at {cc.momento}'
                    self.stdout.write(self.style.WARNING(skipped))

                
            self.stdout.write(self.style.SUCCESS(f'Finished Page {offset}'))
    
        cursor.close()
        connection.close()

        self.stdout.write(self.style.SUCCESS(f"{c} procesados"))
