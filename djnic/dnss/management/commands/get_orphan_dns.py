from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from dnss.models import DNS


class Command(BaseCommand):
    help = 'Buscar DNSs que no pertenezcan a una empresa'

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS("Buscando DNSs"))
        orphans = DNS.objects.filter(empresa_regex__isnull=True)

        pending = orphans.annotate(total_dominios=Count('dominios', filter=Q(dominios__orden=1))).order_by('-total_dominios')[:30]

        for p in pending:
            self.stdout.write(self.style.WARNING(f'{p.dominio} {p.total_dominios}'))
            
        self.stdout.write(self.style.SUCCESS("FIN"))
