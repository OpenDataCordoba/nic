import mysql.connector
import sshtunnel
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar dominiod'

    def add_arguments(self, parser):
        parser.add_argument('--limit', nargs='?', type=int, default=10)

    def handle(self, *args, **options):
        limit = options['limit']
        self.stdout.write(self.style.SUCCESS(f'Importando dominios'))
        
        with sshtunnel.SSHTunnelForwarder(
                (settings.OLD_SSH_HOST, settings.OLD_SSH_PORT),
                ssh_username=settings.OLD_SSH_USER,
                ssh_password=settings.OLD_SSH_PASS,
                remote_bind_address=('localhost', 3306),
                local_bind_address=('localhost', 3306)
        ) as tunnel:

            connection = mysql.connector.connect(
                user=settings.OLD_DB_USER,
                password=settings.OLD_DB_PASS,
                host='localhost',
                database=settings.OLD_DB_NAME,
                port=3306)


            cursor = connection.cursor()
            cursor.execute('Select * from dominios limit 10')

            for dominio in cursor:
                print(f"Dominios {dominio}")

            cursor.close()
            connection.close()

