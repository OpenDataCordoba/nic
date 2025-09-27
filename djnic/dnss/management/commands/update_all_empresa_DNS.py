from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from dnss.models import Empresa


class Command(BaseCommand):
    help = 'Buscar DNSs que no pertenezcan a una empresa'

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS("Buscando Empresas"))

        for empresa in Empresa.objects.all():
            self.stdout.write(self.style.SUCCESS(f'{empresa}'))
            empresa.detect_DNSs()

        self.stdout.write(self.style.SUCCESS("FIN"))
